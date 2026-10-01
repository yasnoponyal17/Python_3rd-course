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
            raise ImportError(f"Не удалось загрузить код из {origin}: {e}")

        code = compile(source, origin, mode="exec")
        exec(code, module.__dict__)


class URLFinder(PathEntryFinder):
    def __init__(self, url):
        self.url = url.rstrip("/")

    def find_spec(self, fullname, target=None):
        name = fullname.rsplit(".", 1)[-1]
        pkg_url = f"{self.url}/{name}/__init__.py"

        try:
            res = requests.head(pkg_url, timeout=3)
            if res.status_code == 200:
                spec = spec_from_loader(
                    fullname,
                    URLLoader(),
                    origin=pkg_url,
                    is_package=True
                )

                spec.submodule_search_locations = [
                    f"{self.url}/{name}"
                ]
                return spec

        except requests.RequestException:
            pass

        mod_url = f"{self.url}/{name}.py"

        try:
            res = requests.head(mod_url, timeout=3)
            if res.status_code == 200:
                return spec_from_loader(
                    fullname,
                    URLLoader(),
                    origin=mod_url,
                    is_package=False
                )

        except requests.RequestException:
            pass

        return None


def url_hook(some_str):
    if not some_str.startswith(("http://", "https://")):
        raise ImportError

    return URLFinder(some_str)


if url_hook not in sys.path_hooks:
    sys.path_hooks.append(url_hook)

print("Хук с поддержкой импорта пакетов зарегистрирован!")