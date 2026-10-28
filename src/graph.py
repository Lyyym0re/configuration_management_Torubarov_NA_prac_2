"""Тестовый репозиторий и рекурсивный обход в ширину."""

import json
from pathlib import Path
import re

TEST_VERSION = "1.0.0"


def check_test(data):
    """Проверить имена, списки зависимостей и отсутствие битых ссылок."""
    for name, children in data.items():
        if not re.fullmatch(r"[A-Z]+", name):
            raise ValueError("Тестовые имена должны состоять из A-Z")
        if not isinstance(children, list):
            raise ValueError(f"У {name} ожидается список зависимостей")
        if any(not isinstance(child, str) for child in children):
            raise ValueError("Имена зависимостей должны быть строками")
        if any(child not in data for child in children):
            raise ValueError(f"У {name} есть ссылка на отсутствующий пакет")


def read_test(filename):
    """Прочитать граф вида {A: [B, C]}; тестовые версии равны 1.0.0."""
    data = json.loads(Path(filename).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("Тестовый репозиторий должен быть JSON-объектом")
    check_test(data)
    return {(name, TEST_VERSION): [(child, TEST_VERSION) for child in children]
            for name, children in data.items()}


def visit(frontier, children, graph, seen):
    """Обработать весь уровень BFS, затем рекурсивно перейти к следующему."""
    if not frontier:
        return
    following = []
    for node in frontier:
        graph[node] = list(dict.fromkeys(children(node)))
        for child in graph[node]:
            if child not in seen:
                seen.add(child)
                following.append(child)
    visit(following, children, graph, seen)


def build(root, children):
    """Построить достижимый граф; seen защищает от циклов и повторов."""
    graph = {}
    visit([root], children, graph, {root})
    return graph


def show(graph):
    """Вывести узлы и связи в порядке обхода BFS."""
    for node, children in graph.items():
        targets = ", ".join(f"{name} {version}" for name, version in children)
        print(f"{node[0]} {node[1]} -> {targets or '(нет зависимостей)'}")
