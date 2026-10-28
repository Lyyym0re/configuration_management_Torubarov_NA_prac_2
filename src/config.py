"""Шесть параметров задания и их проверка."""

import argparse
from pathlib import Path
import re
from urllib.parse import urlsplit

from src.versions import normalize

MAX_NAME = 100


class Parser(argparse.ArgumentParser):
    """Позволить интерактивному режиму продолжить работу после ошибки."""

    def error(self, message):
        """Вместо завершения процесса сообщить об ошибке параметров."""
        raise ValueError(message)


def package_name(name):
    """Проверить допустимые символы и длину имени NuGet-пакета."""
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", name):
        raise ValueError(f"Неверное имя пакета: {name}")
    if len(name) > MAX_NAME:
        raise ValueError("Имя пакета длиннее 100 символов")
    return name


def check_repository(value, test_mode):
    """Проверить существование тестового файла либо HTTP(S)-адрес."""
    if test_mode:
        if not Path(value).is_file():
            raise ValueError("Тестовый файл не найден")
        return
    url = urlsplit(value)
    _ = url.port
    if url.scheme not in ("http", "https") or not url.hostname:
        raise ValueError("Репозиторий должен быть HTTP(S)-адресом")
    if any(char.isspace() for char in value):
        raise ValueError("URL содержит пробелы")


def parse(arguments):
    """Прочитать обязательные параметры и флаги командной строки."""
    parser = Parser(description="NuGet, вариант 23")
    parser.add_argument("-p", "--package", required=True)
    parser.add_argument("-v", "--version", required=True)
    parser.add_argument("-r", "--repository", required=True)
    parser.add_argument("-t", "--test-mode", action="store_true")
    parser.add_argument("-o", "--output", default="graph.png")
    parser.add_argument("-a", "--ascii", action="store_true")
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--root", nargs=2)
    args = parser.parse_args(arguments)
    if args.root:
        package_name(args.root[0])
        args.root[1] = normalize(args.root[1])
    package_name(args.package)
    args.version = normalize(args.version)
    check_repository(args.repository, args.test_mode)
    output = Path(args.output)
    if output.suffix.lower() != ".png" or output.is_dir():
        raise ValueError("Выходной файл должен иметь расширение .png")
    if not output.parent.is_dir() or re.search(r'[<>:"|?*]', output.name):
        raise ValueError("Неверное имя файла или выходная папка не существует")
    return args
