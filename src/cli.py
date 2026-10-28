"""Запуск анализа и простой ввод команд для демонстрации."""

from pathlib import Path
import shlex
import subprocess
import sys
from xml.etree.ElementTree import ParseError

from src.config import Parser, parse
from src.nuget import NuGet
from src.graph import build, read_test, show

ERRORS = (ValueError, OSError, KeyError, TypeError, ParseError,
          subprocess.SubprocessError, RecursionError)


def source(args):
    """Получить корневой узел и функцию чтения его соседей."""
    name = args.package if args.test_mode else args.package.lower()
    root = name, args.version
    if args.test_mode:
        data = read_test(args.repository)
        if root not in data:
            raise ValueError("Нет такого тестового пакета или версии 1.0.0")
        return root, data.__getitem__, data
    return root, NuGet(args.repository).children, None


def run(arguments):
    """Выполнить основной сценарий текущего этапа."""
    args = parse(arguments)
    root, children, _ = source(args)
    show(build(root, children))


def checked(arguments):
    """Показать понятную ошибку и вернуть ненулевой код завершения."""
    try:
        run(arguments)
        return 0
    except SystemExit as error:
        return error.code
    except ERRORS as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2


def command(line):
    """Разобрать analyze, help или вручную введённый exit."""
    try:
        words = shlex.split(line)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return True
    if not words:
        return True
    if words == ["exit"]:
        return False
    if words == ["help"]:
        print("analyze <параметры>; analyze --help; exit")
    elif words[0] == "analyze":
        checked(words[1:])
    else:
        print("Неизвестная команда. Введите help.")
    return True


def shell(lines=()):
    """Выполнить примеры, затем оставить программу для ручного ввода."""
    for line in lines:
        if line.strip():
            print(f"nuget> {line}", flush=True)
            if not command(line):
                return
    while True:
        try:
            if not command(input("nuget> ")):
                return
        except (EOFError, KeyboardInterrupt):
            return


def main(arguments=None):
    """Выбрать опции CLI, интерактивный ввод или файл демонстрации."""
    arguments = sys.argv[1:] if arguments is None else arguments
    if not arguments:
        shell()
        return 0
    if arguments[0] != "--demo":
        return checked(arguments)
    parser = Parser()
    parser.add_argument("--demo", required=True)
    try:
        filename = parser.parse_args(arguments).demo
        shell(Path(filename).read_text(encoding="utf-8-sig").splitlines())
    except ERRORS as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    return 0
