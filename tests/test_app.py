"""Небольшие проверки основных требований текущего этапа."""

from contextlib import redirect_stdout
import io
from pathlib import Path
import unittest
from unittest.mock import patch

from src.config import parse
from src.cli import command
from src.nuget import NuGet

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


if __name__ == "__main__":
    unittest.main()
