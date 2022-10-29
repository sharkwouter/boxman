from typing import Optional

from boxman import Config
from boxman.database import Database
from boxman.desc import Desc


class DatabaseManager:
    def __init__(self, config: Config, refresh_after: int = 30):
        """

        :param refresh_after: Refresh the database after the specified amount of minutes
        """
        self.databases = []
        for repository in config.repositories:
            self.databases.append(Database(repository, refresh_after))

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

    def install_package(self, package: str) -> bool:
        pass

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
