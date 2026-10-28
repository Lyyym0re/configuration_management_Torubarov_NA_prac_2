"""Прямые HTTP-запросы к NuGet V3 и разбор XML-манифестов."""

from functools import cache
import json
from urllib.parse import quote
from urllib.request import urlopen
from xml.etree import ElementTree as ET

from src.config import package_name
from src.versions import normalize

TIMEOUT = 15


@cache
def get(url):
    """Загрузить адрес с таймаутом; повторный запрос взять из памяти."""
    with urlopen(url, timeout=TIMEOUT) as response:
        return response.read()


class NuGet:
    """Получать зависимости без менеджеров пакетов и сторонних библиотек."""

    def __init__(self, url):
        """Найти адрес хранилища пакетов в сервисном индексе."""
        resources = json.loads(get(url))["resources"]
        self.base = next((r["@id"] for r in resources
                          if r.get("@type") == "PackageBaseAddress/3.0.0"), "")
        if not self.base.startswith(("http://", "https://")):
            raise ValueError("В индексе нет PackageBaseAddress/3.0.0")
        self.base = self.base.rstrip("/")

    def dependencies(self, node):
        """Прочитать зависимости точной версии, сохранив группы платформ."""
        name, version = node
        name = quote(package_name(name).lower(), safe="")
        version = quote(normalize(version), safe="")
        url = f"{self.base}/{name}/{version}/{name}.nuspec"
        root = ET.fromstring(get(url))
        for element in root.iter():
            element.tag = element.tag.rsplit("}", 1)[-1]
        metadata = root.find("metadata")
        if metadata is None:
            raise ValueError("В nuspec отсутствует metadata")
        actual = metadata.findtext("id", "").lower()
        if actual != node[0].lower():
            raise ValueError("Получен манифест другого пакета")
        if normalize(metadata.findtext("version", "")) != normalize(node[1]):
            raise ValueError("Получен манифест другой версии")
        dependencies = metadata.find("dependencies")
        if dependencies is None:
            return []
        groups = dependencies.findall("group") or [dependencies]
        return [(package_name(dep.attrib["id"]).lower(),
                 dep.get("version") or "(,)",
                 group.get("targetFramework", "all"))
                for group in groups for dep in group.findall("dependency")]
