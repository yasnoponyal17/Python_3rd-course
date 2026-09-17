import sys
import re
import requests
from importlib.abc import PathEntryFinder, Loader
from importlib.util import spec_from_loader

class URLLoader(Loader):
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        origin = module.__spec__.origin
        try:
            response = requests.get(origin, timeout=3)
            response.raise_for_status()
            source = response.text
        except requests.RequestException as e:
            raise ImportError(f"Не удалось загрузить модуль из {origin}: {e}")

        code = compile(source, origin, mode="exec")
        exec(code, module.__dict__)


class URLFinder(PathEntryFinder):
    def __init__(self, url, available):
        self.url = url
        self.available = available

    def find_spec(self, name, target=None):
        if name in self.available:
            origin = f"{self.url}/{name}.py"
            loader = URLLoader()
            return spec_from_loader(name, loader, origin=origin)
        return None


def url_hook(some_str):
    if not some_str.startswith(("http://", "https://")):
        raise ImportError

    try:
        response = requests.get(some_str, timeout=3)
        response.raise_for_status()
        data = response.text
    except requests.RequestException as e:
        print(f"\n[url_hook] Предупреждение: Хост '{some_str}' недоступен ({e}). Пропускаем...")
        raise ImportError

    filenames = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*\.py', data)
    modnames = {name[:-3] for name in filenames}

    return URLFinder(some_str, modnames)

if url_hook not in sys.path_hooks:
    sys.path_hooks.append(url_hook)

print("Хук зарегистрирован! Текущие path_hooks:", sys.path_hooks)