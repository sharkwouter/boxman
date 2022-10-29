import os.path
import tarfile
import urllib.request
from typing import Optional, List
from urllib.parse import urljoin

from boxman import Config
from boxman.checksums import checksums_match
from boxman.database import Database
from boxman.desc import Desc
from boxman.local_database import LocalDatabase
from boxman.repository import Repository


class DatabaseManager:
    def __init__(
        self, local_database: LocalDatabase, config: Config, refresh_after: int = 1800
    ):
        """

        :param refresh_after: Refresh the database after the specified amount of minutes
        """
        self.local_database = local_database
        self.databases = []
        for repository in config.repositories:
            self.databases.append(Database(repository, refresh_after))
        self.download_directory = config.options.cache_dir
        self.root_dir = config.options.root_dir

    def get_package_list(self, repository: str):
        packages = []
        repository_exists = False
        for database in self.databases:
            if not repository or database.repository.name == repository:
                repository_exists = True
                for package in database.get_package_list():
                    if package not in packages:
                        packages.append(package)

        if not repository_exists:
            print(f'error: repository "{repository}" was not found.')
            exit(1)

        return packages

    def get_installed_list(self):
        return self.local_database.get_package_list()

    def search_packages(self, search_string: str):
        packages = []
        for database in self.databases:
            for package in database.search_packages(search_string):
                if package not in packages:
                    packages.append(package)

        packages.sort()

        return packages

    def show_package(self, package: str):
        result = ""
        for database in self.databases:
            result += database.show_package(package)
        if result:
            return result

    def install_package(self, package: str, installed_explicitly=True) -> bool:
        package_description = self.get_package_desc(package)
        if not package_description:
            print(f"Failed to find package {package}")
            return False

        for dependency in package_description.dependencies:
            if not self.local_database.get_desc(dependency):
                self.install_package(dependency, False)

        if not self.local_database.get_desc(package):
            downloaded_archive = self.download_package(package_description)
            if not downloaded_archive:
                return False
            installed_files = self.extract_archive(downloaded_archive)
            self.local_database.write_files_list(package_description, installed_files)
            self.local_database.install_desc(package_description, installed_explicitly)

        return True

    def extract_archive(self, archive: str) -> List[str]:
        files_to_extract = self.get_files_to_extract_from_archive(archive)
        with tarfile.open(archive) as t:
            for member in t.getmembers():
                if member.path in files_to_extract:
                    target = os.path.join(self.root_dir, member.path)
                    if member.isdir():
                        if not os.path.exists(target):
                            os.makedirs(target)
                    else:
                        with open(target, "wb") as target_file:
                            target_file.write(t.extractfile(member).read())

        for file in files_to_extract:
            assert os.path.exists(file)

        return files_to_extract

    def get_files_to_extract_from_archive(self, archive) -> List[str]:
        files = []
        with tarfile.open(archive) as t:
            for member in t.getmembers():
                if member.name.startswith(".") or ".." in member.path:
                    continue
                extract_to = os.path.join(self.root_dir, member.path)
                if len(extract_to) < (len(self.root_dir) + len(member.path) - 1):
                    raise Exception(
                        f"Failed to concatenate {self.root_dir} and {member.path}, result was {extract_to}"
                    )
                files.append(member.path)
        return files

    def get_package_desc(self, package: str) -> Optional[Desc]:
        descs_found = []
        for database in self.databases:
            desc = database.get_desc(package)
            if desc:
                descs_found.append(desc)

        newest_desc = None
        for desc in descs_found:
            if newest_desc is None or desc > newest_desc:
                newest_desc = desc

        return newest_desc

    def download_package(self, desc: Desc) -> Optional[str]:
        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)
        current_repository = self.get_repository(desc.source)
        if not current_repository:
            raise Exception("Failed to find repository")
        download_url = urljoin(current_repository.url, desc.file_name)
        download_path = os.path.join(self.download_directory, desc.file_name)
        if not os.path.isfile(download_path):
            print(f"Downloading {desc.file_name}")
            urllib.request.urlretrieve(download_url, download_path)

        if not checksums_match(download_path, desc.md5_checksum, desc.sha256_checksum):
            os.remove(download_path)
            print(f"Downloaded {desc.name} package did not match checksums in db")
            return None

        return download_path

    def get_repository(self, name: str) -> Optional[Repository]:
        for database in self.databases:
            if database.repository.name == name:
                return database.repository

        print(f"Could not find repository with name {name}")

    def get_installed_package_desc(self, package: str) -> Optional[Desc]:
        return self.local_database.get_desc(package)
