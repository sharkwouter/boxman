import os
import re
import shutil
from typing import List, Optional

from boxman import Config
from boxman.constants import ALPM_DB_VERSION
from boxman.desc import Desc
from boxman.files import Files
from boxman.version import Version


class LocalDatabase:
    __local_directory: str
    config: Config

    def __init__(self, config: Config):
        self.config = config
        self.__local_directory = os.path.join(config.options.db_path, "local")
        if not os.path.isdir(self.__local_directory):
            os.makedirs(self.__local_directory)
            with open(
                os.path.join(self.__local_directory, "ALPM_DB_VERSION"), "w"
            ) as db_version_file:
                db_version_file.write(ALPM_DB_VERSION)

    def get_package_list(self) -> List[str]:
        packages = []
        for member in os.listdir(self.__local_directory):
            full_path = os.path.join(self.__local_directory, member)
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
        installed = os.listdir(self.__local_directory)
        installed.sort()
        for member in installed:
            directory = os.path.join(self.__local_directory, member)
            if os.path.isdir(directory):
                files_path = os.path.join(directory, "file_list")
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
        for member in os.listdir(self.__local_directory):
            if re.match(r"[\w\-._]*-\d[\w.]*-\d+", member):
                full_path = os.path.join(self.__local_directory, member, "desc")
                with open(full_path, "r") as desc_file:
                    result.append(Desc(desc_file.read(), "local"))
        return result

    def get_package_directory(self, package: str) -> Optional[str]:
        for member in os.listdir(self.__local_directory):
            if not re.match(r"[\w\-._]*-\d[\w.]*-\d+", member):
                print(f"{member} does not match")
                continue
            name, version, rel = member.rsplit("-", 2)
            if name == package:
                return os.path.join(self.__local_directory, member)
        return None

    def get_package_version(self, package: str) -> Optional[Version]:
        for member in os.listdir(self.__local_directory):
            if not re.match(r"[\w\-._]*-\d[\w.]*-\d+", member):
                continue
            name, version, rel = member.rsplit("-", 2)
            if name == package:
                return Version(f"{version}-{rel}")
        return None

    def get_package_desc(self, package: str) -> Optional[Desc]:
        for member in os.listdir(self.__local_directory):
            if re.match(rf"^{package}-\d[\w.]*-\d+", member):
                full_path = os.path.join(self.__local_directory, member, "desc")
                with open(full_path, "r") as desc_file:
                    return Desc(desc_file.read(), "local")

    def get_package_files(self, package) -> Optional[Files]:
        directory = self.get_package_directory(package)
        if directory:
            with open(os.path.join(directory, "files")) as files_file:
                return Files(self.config.options.root_dir, files_file.read())
        return None

    def remove_package(self, package: str) -> bool:
        directory = self.get_package_directory(package)
        if directory:
            shutil.rmtree(directory)
            return True
        return False

    def install(
        self, desc: Desc, files: Files, installed_explicitly: bool = True
    ) -> None:
        directory = os.path.join(self.__local_directory, f"{desc.name}-{desc.version}")
        if not os.path.isdir(directory):
            os.makedirs(directory)
        desc.convert_to_local(installed_explicitly)
        with open(os.path.join(directory, "desc"), "w") as desc_file:
            desc_file.write(repr(desc))
        with open(os.path.join(directory, "files"), "w") as files_file:
            files_file.write(repr(files))
