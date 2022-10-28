from typing import List

from boxman.config import Config
from boxman.args_parser import ParsedArguments
from boxman.data.mode import Mode
from boxman.database_manager import DatabaseManager


class Boxman:
    def __init__(self, config: Config, database_manager: DatabaseManager):
        self.config = config
        self.database_manager = database_manager

    def run(self, args: ParsedArguments) -> None:  # noqa: C901
        if args.mode == Mode.INSTALL:
            self.__run_install(args.arguments)
        elif args.mode == Mode.UPDATE:
            self.__run_update(args.arguments)
        elif args.mode == Mode.REMOVE:
            self.__run_remove(args.arguments)
        elif args.mode == Mode.SEARCH:
            self.__run_search(args.arguments[0])
        elif args.mode == Mode.SHOW:
            self.__run_show(args.arguments[0])
        elif args.mode == Mode.LIST:
            self.__run_list(args.arguments[0])
        elif args.mode == Mode.INSTALLED:
            self.__run_installed()
        elif args.mode == Mode.NOT_SET:
            raise ValueError("Mode was not set")

    def __run_install(self, packages: List[str]) -> None:
        failed = False
        for package in packages:
            if self.database_manager.install_package(package):
                print(f"Installed {package} successfully")
            else:
                failed = True
                print(f"Failed to install {package}")
        if failed:
            exit(1)

    def __run_update(self, packages: List[str]) -> None:
        pass

    def __run_remove(self, packages: List[str]) -> None:
        pass

    def __run_search(self, search_string: str) -> None:
        packages = self.database_manager.search_packages(search_string)
        for package in packages:
            print(package)

    def __run_show(self, package: str) -> None:
        result = self.database_manager.show_package(package)
        if result:
            print(result, end="")
        else:
            print(f"package {package} not found")
            exit(1)

    def __run_list(self, repository: str) -> None:
        packages = self.database_manager.get_package_list(repository)
        for package in packages:
            print(package)

    def __run_installed(self) -> None:
        pass
