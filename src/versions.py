"""Нормализация версий и выбор версии по диапазону NuGet."""

import re

VERSION = (r"\d+(?:\.\d+){0,3}"
           r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
           r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?")
PARTS = 4
PAIR = 2


def normalize(version):
    """Убрать метаданные, лишние нули и дополнить номер до трёх частей."""
    if not isinstance(version, str) or not re.fullmatch(VERSION, version):
        raise ValueError(f"Некорректная версия: {version}")
    number, mark, suffix = version.split("+", 1)[0].partition("-")
    parts = [str(int(part)) for part in number.split(".")]
    parts += ["0"] * (PARTS - len(parts))
    if parts[-1] == "0":
        parts.pop()
    return ".".join(parts) + (mark + suffix.lower() if mark else "")
