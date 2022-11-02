import os.path
import re
import sys
from configparser import ConfigParser, SectionProxy
from typing import List

from boxman.constants import APPLICATION_NAME
from boxman.data.options import Options
from boxman.repository import Repository


class Config:
    options: Options
    repositories: List[Repository]
    __base_directory: str

    def __init__(self, base_directory: str) -> None:
        self.__base_directory = base_directory
        self.repositories = []
        self.__set_options_defaults()
        self.__parse_config()

    def __set_options_defaults(self) -> None:
        root_dir = self.base_directory
        cache_dir = os.path.join(
            self.base_directory, "var", "cache", APPLICATION_NAME, "pkg"
        )
        db_path = os.path.join(self.base_directory, "var", "lib", APPLICATION_NAME)
        self.options = Options(root_dir=root_dir, cache_dir=cache_dir, db_path=db_path)

    def __parse_config(self) -> None:
        parser = ConfigParser(
            allow_no_value=True,
            comment_prefixes=["#"],
        )
        config_file = os.path.join(
            self.base_directory, "etc", f"{APPLICATION_NAME}.conf"
        )
        if os.path.isfile(config_file):
            parser.read(config_file)
        else:
            sys.exit(f"Configuration file {config_file} not found")

        for section in parser.sections():
            if section == "options":
                self.__parse_config_options(parser["options"])
            else:
                self.__parse_config_repository(parser[section])

    def __parse_config_options(self, options_section: SectionProxy) -> None:
        for key in options_section.keys():
            if key == "rootdir":
                self.options.root_dir = self.get_root_path(
                    options_section.get("rootdir")
                )
            elif key == "cachedir":
                self.options.cache_dir = self.get_relative_path(
                    options_section.get("cachedir")
                )
            elif key == "dbpath":
                self.options.db_path = self.get_relative_path(
                    options_section.get("dbpath")
                )

    def __parse_config_repository(self, section: SectionProxy) -> None:
        # Make sure the required variables are set
        if not re.match(r"^[a-zA-Z_\-]+$", section.name):
            print(f"{section.name} is not a valid repository name")
            return
        if not section.get("Server"):
            print(f"Server url for repository {section.name} is not valid")
            return

        self.repositories.append(
            Repository(section.name, section.get("Server"), self.options.db_path)
        )

    def get_relative_path(self, path: str) -> str:
        """
        Takes in any path string and returns a relative path within the base directory
        :param path: The path which needs to be sanitized
        :return: full path inside the base directory
        """
        # Remove starting  drive letter on Windows
        if sys.platform == "win32":
            if re.match(r"^[A-Z]:[/\\].*", path):
                path = path[3:]

        # Do not allow ..
        path = path.replace("..", "")

        # Do no allow path to start with a /
        while path.startswith(("/", "\\")):
            path = path[1:]

        assert self.options.root_dir
        return os.path.join(self.options.root_dir, path)

    def get_root_path(self, path: str) -> str:
        """
        Takes the root path string and returns the full path
        This can be relative to the base directory or absolute
        :param path: The path which needs to be sanitized
        :return: full path inside the base directory
        """
        path = os.path.expanduser(os.path.expandvars(path))
        if "$" in path:
            raise Exception(
                f"Could not expand {path} because an environment variable is not set"
            )
        full_path = os.path.join(self.base_directory, path)
        assert (
            full_path
            and full_path != os.sep
            and not re.match("^[A-Za-z]:\\$", full_path)
        )
        return full_path

    @property
    def base_directory(self) -> str:
        return self.__base_directory
