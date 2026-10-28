"""Небольшие проверки основных требований текущего этапа."""

from contextlib import redirect_stdout
import io
from pathlib import Path
import unittest
from unittest.mock import patch

from src.config import parse
from src.cli import command
from src.nuget import NuGet
from src.versions import choose
from src.graph import build, read_test
from src.visual import plantuml, tree

ROOT = Path(__file__).resolve().parents[1]
OPTIONS = ["--package", "A", "--version", "1.0.0", "--test-mode",
           "--repository", str(ROOT / "demo/repository.json")]


class AppTests(unittest.TestCase):
    """Проверять поведение, нужное для демонстрации и защиты."""

    def test_configuration(self):
        """Принимать правильные настройки и отвергать ошибки параметров."""
        self.assertEqual(parse(OPTIONS).version, "1.0.0")
        invalid = (["--package", "bad name"], ["--version", "wrong"],
                   ["--repository", "missing.json"], ["--output", "bad.jpg"],
                   ["--ascii", "yes"], ["--test-mode", "yes"])
        for extra in invalid:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                parse(OPTIONS + extra)
        with self.assertRaises(ValueError):
            parse([])

    def test_manual_input(self):
        """После неизвестной команды можно продолжить ручной ввод."""
        with redirect_stdout(io.StringIO()):
            self.assertTrue(command("unknown"))
            self.assertTrue(command("help"))

    def test_manifest(self):
        """Извлечь прямую зависимость из nuspec без сетевого запроса."""
        xml = (b"<package><metadata><id>A</id><version>1.0</version>"
               b'<dependencies><dependency id="B" version="[2]"/>'
               b"</dependencies></metadata></package>")
        feed = b'{"resources":[{"@type":"PackageBaseAddress/3.0.0",'
        feed += b'"@id":"https://feed.test/"}]}'
        with patch("src.nuget.get", side_effect=[feed, xml]):
            result = NuGet("https://feed.test").dependencies(("a", "1"))
            self.assertEqual(result, [("b", "[2]", "all")])

    def test_version_range(self):
        """Выбирать минимальную версию с учётом открытой верхней границы."""
        self.assertEqual(choose(["2.0", "1.5", "1.0"], "[1.1,2)"), "1.5.0")

    def test_recursive_bfs(self):
        """Получить порядок BFS и не зациклиться на обратной связи."""
        links = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": ["A"]}
        graph = build("A", links.__getitem__)
        self.assertEqual(list(graph), ["A", "B", "C", "D"])
        self.assertEqual(graph["D"], ["A"])

    def test_local_repository(self):
        """Проверить общий потомок, цикл и одиночный тестовый пакет."""
        data = read_test(ROOT / "demo/repository.json")
        for name, count in (("A", 4), ("E", 2), ("G", 1), ("Z", 1)):
            with self.subTest(name=name):
                self.assertEqual(len(build((name, "1.0.0"), data.__getitem__)),
                                 count)

    def test_visualization(self):
        """Сформировать стрелки PlantUML и остановить повтор в дереве."""
        data = read_test(ROOT / "demo/repository.json")
        graph = build(("E", "1.0.0"), data.__getitem__)
        text = plantuml(graph)
        self.assertIn("n0 --> n1", text)
        self.assertIn("n1 --> n0", text)
        output = io.StringIO()
        with redirect_stdout(output):
            tree(graph, ("E", "1.0.0"))
        self.assertIn("[повтор]", output.getvalue())


if __name__ == "__main__":
    unittest.main()
