import os
import re
import shutil
from typing import List, Optional

from boxman.constants import ALPM_DB_VERSION
from boxman.desc import Desc
from boxman.version import Version


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
        return f"{package_name} {package_version}-{package_rel}"

    def get_installed_files(self, package: str) -> List[str]:
        files = []
        installed = os.listdir(self.__dir)
        installed.sort()
        for member in installed:
            directory = os.path.join(self.__dir, member)
            if os.path.isdir(directory):
                files_path = os.path.join(directory, "files")
                if not os.path.isfile(files_path):
                    continue
                with open(files_path, "r") as file:
                    for line in file.read().split("\n"):
                        if not line or line == "%FILES%":
                            continue
                        files.append(f"{member.rsplit('-', 2)[0]} {line}")
        return files

    def get_desc_list(self) -> List[Desc]:
        result = []
        for member in os.listdir(self.__dir):
            if re.match(r"[\w\-._]*-\d[\w.]*-\d+", member):
                full_path = os.path.join(self.__dir, member, "desc")
                with open(full_path, "r") as desc_file:
                    result.append(Desc(desc_file.read(), "local"))
        return result

    def get_desc(self, package: str) -> Optional[Desc]:
        for member in os.listdir(self.__dir):
            if re.match(rf"^{package}-\d[\w.]*-\d+", member):
                full_path = os.path.join(self.__dir, member, "desc")
                with open(full_path, "r") as desc_file:
                    return Desc(desc_file.read(), "local")

    def install_desc(self, desc: Desc, installed_explicitly: bool = True) -> None:
        directory = self.get_desc_directory(desc)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        desc.convert_to_local(installed_explicitly)
        with open(os.path.join(directory, "desc"), "w") as desc_file:
            desc_file.write(repr(desc))

    def write_files_list(self, desc: Desc, files: List[str]):
        directory = self.get_desc_directory(desc)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Prepare list
        lines = ["%FILES%"] + files + [""]

        with open(os.path.join(directory, "files"), "w") as files_file:
            files_file.write("\n".join(lines))

    def get_desc_directory(self, desc: Desc):
        return os.path.join(self.__dir, f"{desc.name}-{desc.version}")

    def get_package_directory_if_installed(self, package: str) -> Optional[str]:
        for member in os.listdir(self.__dir):
            if not re.match(r"[\w\-._]*-\d[\w.]*-\d+", member):
                print(f"{member} does not match")
                continue
            name, version, rel = member.rsplit("-", 2)
            if name == package:
                return os.path.join(self.__dir, member)
        return None

    def get_package_version_if_installed(self, package: str) -> Optional[Version]:
        for member in os.listdir(self.__dir):
            if not re.match(r"[\w\-._]*-\d[\w.]*-\d+", member):
                continue
            name, version, rel = member.rsplit("-", 2)
            if name == package:
                return Version(f"{version}-{rel}")
        return None

    def get_package_files_if_installed(self, package) -> Optional[List[str]]:
        directory = self.get_package_directory_if_installed(package)
        if directory:
            files = []
            with open(os.path.join(directory, "files")) as files_file:
                for file in files_file.read().split("\n"):
                    if not file or file == "%FILES%":
                        continue
                    files.append(file)
            return files
        return None

    def remove_package(self, package: str, root_path: str) -> bool:
        for member in os.listdir(self.__dir):
            full_path = os.path.join(self.__dir, member)
            if (
                os.path.isdir(full_path)
                and re.match(r"[\w\-._]*-\d[\w.]*-\d+", member)
                and member.rsplit("-", 2)[0] == package
            ):
                with open(os.path.join(full_path, "files")) as files_file:
                    for relative_file_path in files_file.read().split("\n"):
                        if not relative_file_path or relative_file_path == "%FILES%":
                            continue
                        full_file_path = os.path.join(root_path, relative_file_path)
                        os.remove(full_file_path)
                shutil.rmtree(full_path)
                return True
        return False
