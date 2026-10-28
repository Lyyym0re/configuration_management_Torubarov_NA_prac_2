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


def version_key(version):
    """Сравнивать числа численно, а prerelease — по правилам SemVer."""
    number, mark, suffix = normalize(version).partition("-")
    parts = tuple(int(part) for part in number.split("."))
    parts += (0,) * (PARTS - len(parts))
    labels = tuple((0, int(p)) if p.isdigit() else (1, p)
                   for p in suffix.split(".")) if mark else ()
    return parts, not bool(mark), labels


def bounds(text):
    """Разобрать минимум 1.0, точную [1.0] или интервал [1.0,2.0)."""
    text = text.strip()
    if not text:
        raise ValueError("Пустое ограничение версии")
    if text[0] not in "[(":
        normalize(text)
        return text, "", True, False
    if text[-1] not in "])":
        raise ValueError(f"Неверный диапазон: {text}")
    if "," not in text:
        if text[0] + text[-1] != "[]":
            raise ValueError(f"Неверный диапазон: {text}")
        value = normalize(text[1:-1])
        return value, value, True, True
    limits = [part.strip() for part in text[1:-1].split(",")]
    if len(limits) != PAIR:
        raise ValueError(f"Неверный диапазон: {text}")
    for value in limits:
        if value:
            normalize(value)
    return *limits, text[0] == "[", text[-1] == "]"


def within(key, limit, inclusive, lower):
    """Проверить одну границу интервала; пустая граница бесконечна."""
    if not limit:
        return True
    bound = version_key(limit)
    if lower:
        return key > bound or (inclusive and key == bound)
    return key < bound or (inclusive and key == bound)


def choose(versions, expression):
    """Выбрать минимальную доступную версию, подходящую диапазону."""
    low, high, include_low, include_high = bounds(expression)
    for version in sorted(versions, key=version_key):
        if "-" in normalize(version) and "-" not in low + high:
            continue
        key = version_key(version)
        fits = within(key, low, include_low, True)
        if fits and within(key, high, include_high, False):
            return normalize(version)
    raise ValueError(f"Нет версии для ограничения {expression}")
