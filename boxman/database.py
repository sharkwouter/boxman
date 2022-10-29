import os
import re
import tarfile
import time
import urllib.request
from typing import Callable, List, Optional

from boxman.desc import Desc
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

        should_refresh = False
        if (
            not os.path.isfile(self.repository.path)
            or not tarfile.is_tarfile(self.repository.path)
            or force
        ):
            should_refresh = True
        else:
            time_since_last_refresh = int(
                time.time() - os.path.getmtime(self.repository.path)
            )
            if time_since_last_refresh > self.refresh_after:
                should_refresh = True

        if should_refresh:
            print(f"Downloading database {self.repository.name}")
            urllib.request.urlretrieve(self.repository.url, self.repository.path)

    @refresh_if_needed
    def get_package_list(self) -> List[str]:
        packages = []
        with tarfile.open(self.repository.path) as t:
            for member in t.getmembers():
                if member.isdir():
                    package = self.__directory_to_package_list_entry(member.name)
                    packages.append(package)
        packages.sort()
        return packages

    @refresh_if_needed
    def search_packages(self, search_string: str) -> List[str]:
        packages = []
        with tarfile.open(self.repository.path) as t:
            for member in t.getmembers():
                if member.isdir():
                    package = self.__directory_to_package_list_entry(member.name)
                    if search_string in package.split(" ")[0]:
                        packages.append(package)
        return packages

    def show_package(self, package: str) -> Optional[str]:
        result = ""
        for desc in self.get_desc_list():
            if not package or desc.name == package:
                result += str(desc)
        return result

    def __directory_to_package_list_entry(self, name: str) -> str:
        if re.match(r"[\w\-_]+ [\d\-.]+]", name):
            return name
        package_name, package_version, package_rel = name.rsplit("-", 2)
        return f"{self.repository.name} {package_name} {package_version}-{package_rel}"

    @refresh_if_needed
    def get_desc_list(self) -> List[Desc]:
        result = []
        with tarfile.open(self.repository.path) as t:
            for member in t.getmembers():
                if re.match(r"[\w\-._]*-\d[\w.]*-\d+/desc", member.path):
                    content = t.extractfile(member).read().decode()
                    result.append(Desc(content, self.repository.name))
        return result

    @refresh_if_needed
    def get_desc(self, package: str) -> Optional[Desc]:
        with tarfile.open(self.repository.path) as t:
            for member in t.getmembers():
                if re.match(rf"^{package}-[\w.]*-\d+/desc", member.path):
                    content = t.extractfile(member).read().decode()
                    return Desc(content, self.repository.name)
