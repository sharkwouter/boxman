from typing import List

from boxman import Config
from boxman import ParsedArguments
from boxman.data.mode import Mode


class Boxman:
    def __init__(self, config: Config):
        self.config = config

    def run(self, args: ParsedArguments) -> None:
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
            self.__run_list()
        elif args.mode == Mode.INSTALLED:
            self.__run_installed()
        elif args.mode == Mode.NOT_SET:
            raise ValueError("Mode was not set")

    def __run_install(self, packages: List[str]) -> None:
        pass

    def __run_update(self, packages: List[str]) -> None:
        pass

    def __run_remove(self, packages: List[str]) -> None:
        pass

    def __run_search(self, string: str) -> None:
        pass

    def __run_show(self, package: str) -> None:
        pass

    def __run_list(self) -> None:
        pass

    def __run_installed(self) -> None:
        pass
