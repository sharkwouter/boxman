import os
import re
from typing import List, Optional

from boxman.constants import ALPM_DB_VERSION
from boxman.desc import Desc


class LocalDatabase:
    __dir: str

    def __init__(self, db_path: str):
        self.__dir = os.path.join(db_path, "local")
        if not os.path.isdir(self.__dir):
            os.makedirs(self.__dir)
            with open(
                os.path.join(self.__dir, "ALPM_DB_VERSION"), "w"
            ) as db_version_file:
                db_version_file.write(ALPM_DB_VERSION)

    def get_package_list(self) -> List[str]:
        packages = []
        for member in os.listdir(self.__dir):
            full_path = os.path.join(self.__dir, member)
            if os.path.isdir(full_path):
                package = self.__directory_to_package_list_entry(member)
                packages.append(package)
        packages.sort()
        return packages

    def __directory_to_package_list_entry(self, name: str) -> str:
        if re.match(r"[\w\-_]+ [\d\-.]+]", name):
            return name
        package_name, package_version, package_rel = name.rsplit("-", 2)
        return f"local {package_name} {package_version}-{package_rel}"

    def get_desc_list(self) -> List[Desc]:
        result = []
        for member in os.listdir(self.__dir):
            if re.match(r"[\w\-._]*-\d[\w.]*-\d+/desc", member):
                full_path = os.path.join(self.__dir, member)
                with open(full_path, "r") as desc_file:
                    result.append(Desc(desc_file.read(), "local"))
        return result

    def get_desc(self, package: str) -> Optional[Desc]:
        for member in os.listdir(self.__dir):
            if re.match(rf"^{package}-\d[\w.]*-\d+/desc", member):
                full_path = os.path.join(self.__dir, member)
                with open(full_path, "r") as desc_file:
                    return Desc(desc_file.read(), "local")

    def install_desc(self, desc: Desc, installed_explicitly: bool = True) -> None:
        directory = os.path.join(self.__dir, f"{desc.name}-{desc.version}")
        if os.path.exists(directory):
            print(f"package {desc.name} version {desc.version} is already installed")
            return

        os.makedirs(directory)
        desc.convert_to_local(installed_explicitly)
        with open(os.path.join(directory, "desc"), "w") as desc_file:
            desc_file.write(repr(desc))
