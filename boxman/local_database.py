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

    def get_installed_packages(self) -> List[str]:
        packages = []
        for package_directory in self.get_package_directories():
            packages.append(package_directory.rsplit("-", 2)[0])
        return packages

    def get_installed_files(
        self, package: Optional[str] = None
    ) -> Optional[List[Files]]:
        if package:
            return [self.get_package_files(package)]

        files = []
        for package in self.get_installed_packages():
            files.append(self.get_package_files(package))

        return files

    def get_desc_list(self) -> List[Desc]:
        result = []
        for member in self.get_package_directories():
            full_path = os.path.join(self.__local_directory, member, "desc")
            with open(full_path, "r") as desc_file:
                result.append(Desc(desc_file.read(), "local"))
        return result

    def get_package_directories(self) -> List[str]:
        package_directories = []
        for member in os.listdir(self.__local_directory):
            if os.path.isdir(os.path.join(self.__local_directory, member)) and re.match(
                r"[\w\-._]+-[\w.]+-\d+", member
            ):
                package_directories.append(member)

        return package_directories

    def get_package_directory(self, package: str) -> Optional[str]:
        for member in self.get_package_directories():
            if re.match(rf"^{package}-[\w.]+-\d+$", member):
                return member
        return None

    def get_package_version(self, package: str) -> Optional[Version]:
        package_directory = self.get_package_directory(package)
        if package_directory:
            name, version, rel = package_directory.rsplit("-", 2)
            if name == package:
                return Version(f"{version}-{rel}")
        return None

    def get_package_desc(self, package: str) -> Optional[Desc]:
        package_directory = self.get_package_directory(package)
        if package_directory:
            full_path = os.path.join(self.__local_directory, package_directory, "desc")
            with open(full_path, "r") as desc_file:
                return Desc(desc_file.read(), "local")

    def get_package_files(self, package) -> Optional[Files]:
        package_directory = self.get_package_directory(package)
        if package_directory:
            files_path = os.path.join(
                self.__local_directory, package_directory, "files"
            )
            with open(files_path) as files_file:
                return Files(
                    package, self.config.options.root_dir, content=files_file.read()
                )
        return None

    def remove_package(self, package: str) -> bool:
        package_directory = self.get_package_directory(package)
        if package_directory:
            shutil.rmtree(package_directory)
            return True
        return False

    def install(
        self, desc: Desc, files: Files, installed_explicitly: bool = True
    ) -> None:
        package_directory = os.path.join(
            self.__local_directory, f"{desc.name}-{desc.version}"
        )
        if not os.path.isdir(package_directory):
            os.makedirs(package_directory)
        desc.convert_to_local(installed_explicitly)
        with open(os.path.join(package_directory, "desc"), "w") as desc_file:
            desc_file.write(repr(desc))
        with open(os.path.join(package_directory, "files"), "w") as files_file:
            files_file.write(repr(files))
