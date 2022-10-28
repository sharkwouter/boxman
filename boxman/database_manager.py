from boxman import Config
from boxman.database import Database


class DatabaseManager:
    def __init__(self, config: Config, refresh_after: int = 30):
        """

        :param refresh_after: Refresh the database after the specified amount of minutes
        """
        self.databases = []
        for repository in config.repositories:
            self.databases.append(Database(repository, refresh_after))

    def get_package_list(self):
        packages = []
        for database in self.databases:
            for package in database.get_package_list():
                if package not in packages:
                    packages.append(package)

        packages.sort()

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
        return not package
