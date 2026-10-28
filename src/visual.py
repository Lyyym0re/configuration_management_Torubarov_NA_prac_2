"""PlantUML, PNG и ASCII-дерево без бесконечного раскрытия циклов."""

import os
from pathlib import Path
import subprocess

JAR = Path(__file__).resolve().parents[1] / ".tools/plantuml.jar"
PNG = b"\x89PNG\r\n\x1a\n"
TIMEOUT = 90


def label(node):
    """Подписать пакет вместе с его версией."""
    return f"{node[0]} {node[1]}"


def plantuml(graph):
    """Назначить узлам короткие псевдонимы и сохранить все стрелки."""
    ids = {node: f"n{index}" for index, node in enumerate(graph)}
    lines = ["@startuml", "left to right direction", "scale max 6000*6000"]
    for node, alias in ids.items():
        lines.append(f'rectangle "{label(node)}" as {alias}')
    for node, children in graph.items():
        lines += [f"{ids[node]} --> {ids[child]}" for child in children]
    return "\n".join(lines + ["@enduml", ""])


def save(graph, filename):
    """Сохранить исходник и локально преобразовать его в PNG через Java."""
    path = Path(filename)
    source = plantuml(graph)
    path.with_suffix(".puml").write_text(source, encoding="utf-8")
    jar = os.environ.get("PLANTUML_JAR", str(JAR))
    if not Path(jar).is_file():
        raise ValueError("Нет PlantUML: выполните tools/setup_render.ps1")
    command = [os.environ.get("JAVA_BIN", "java"),
               "-Djava.awt.headless=true", "-DPLANTUML_LIMIT_SIZE=8192",
               "-jar", jar, "-charset", "UTF-8", "-tpng", "-pipe", "-failfast2"]
    result = subprocess.run(command, input=source.encode("utf-8"),
                            capture_output=True, timeout=TIMEOUT, check=False)
    if result.returncode or not result.stdout.startswith(PNG):
        raise ValueError("PlantUML не создал PNG; проверьте Java и JAR")
    path.write_bytes(result.stdout)
    print(f"Сохранены {path.with_suffix('.puml')} и {path}")


def tree(graph, node, prefix="", seen=None):
    """Вывести дерево; [повтор] обозначает общий узел или замыкание цикла."""
    if seen is None:
        seen = {node}
        print(label(node))
    children = graph[node]
    last = len(children) - 1
    for index, child in enumerate(children):
        end = index == last
        repeated = child in seen
        branch = "\\-- " if end else "|-- "
        marker = " [повтор]" if repeated else ""
        print(prefix + branch + label(child) + marker)
        if not repeated:
            seen.add(child)
            tree(graph, child, prefix + ("    " if end else "|   "), seen)
