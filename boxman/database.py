import os
import re
import tarfile
import time
import urllib
from typing import Callable, List, Optional

from boxman.repository import Repository


def refresh_if_needed(func: Callable):
    def inner(self, *args, **kwargs):
        self.refresh()
        return func(self, *args, **kwargs)

    return inner


class Database:
    def __init__(self, repository: Repository, refresh_after: int = 1800):
        self.repository = repository
        self.refresh_after = refresh_after

    def refresh(self, force=False) -> None:
        if not os.path.isdir(self.repository.dir):
            os.makedirs(self.repository.dir)

        if (
            not tarfile.is_tarfile(self.repository.path)
            or self.refresh_after
            > (time.time() - os.path.getmtime(self.repository.path))
            or force
        ):
            print(f"Downloading database {self.repository.name}")
            urllib.request.urlretrieve(self.repository.url, self.repository.path)

    @refresh_if_needed
    def get_package_list(self) -> List[str]:
        packages = []
        with tarfile.open(self.repository.path) as t:
            for member in t.getmembers():
                if member.isdir():
                    package = self.__sanitize_package_list_entry(member.name)
                    packages.append(package)
        return packages

    @refresh_if_needed
    def search_packages(self, search_string: str) -> List[str]:
        packages = []
        with tarfile.open(self.repository.path) as t:
            for member in t.getmembers():
                if member.isdir():
                    package = self.__sanitize_package_list_entry(member.name)
                    if search_string in package.split(" ")[0]:
                        packages.append(package)
        return packages

    @refresh_if_needed
    def show_package(self, package: str) -> Optional[str]:
        if not package.endswith("-") and not package.endswith("."):
            with tarfile.open(self.repository.path) as t:
                for member in t.getmembers():
                    if re.match(rf"{package}[\-\d.]*/desc", member.path):
                        return t.extractfile(member).read().decode()
        return None

    @staticmethod
    def __sanitize_package_list_entry(name: str) -> str:
        if " " in name:
            return name
        package_name, package_version, package_rel = name.rsplit("-", 2)
        return f"{package_name} {package_version}-{package_rel}"
