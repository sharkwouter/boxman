import os.path
import re
import sys
from configparser import ConfigParser, SectionProxy
from typing import List

from boxman.constants import APPLICATION_NAME
from boxman.data.config.options import Options
from boxman.data.config.repository import Repository


class Config:
    options: Options
    repositories: List[Repository]
    __base_directory: str

    def __init__(self, base_directory: str):
        self.__base_directory = base_directory
        self.repositories = []
        self.__set_options_defaults()
        self.__parse_config()

    def __set_options_defaults(self):
        root_dir = self.base_directory
        cache_dir = os.path.join(self.base_directory, "var", "cache", APPLICATION_NAME, "pkg")
        db_path = os.path.join(self.base_directory, "var", "lib", APPLICATION_NAME)
        self.options = Options(
            root_dir=root_dir,
            cache_dir=cache_dir,
            db_path=db_path
        )

    def __parse_config(self):
        parser = ConfigParser(allow_no_value=True, comment_prefixes=['#'], )
        parser.read(os.path.join(self.base_directory, "etc", f"{APPLICATION_NAME}.conf"))

        for section in parser.sections():
            if section == "options":
                self.__parse_config_options(parser["options"])
            else:
                self.__parse_config_repository(parser[section])

    def __parse_config_options(self, options_section: SectionProxy):
        for key in options_section.keys():
            if key == "rootdir":
                self.options.root_dir = self.get_relative_path(options_section.get("rootdir"))
            elif key == "cachedir":
                self.options.cache_dir = self.get_relative_path(options_section.get("cachedir"))
            elif key == "dbpath":
                self.options.db_path = self.get_relative_path(options_section.get("dbpath"))

    def __parse_config_repository(self, section: SectionProxy):
        self.repositories.append(Repository(section.name, section.get("Server")))

    def get_relative_path(self, path: str):
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

        return os.path.join(self.base_directory, path)

    @property
    def base_directory(self) -> str:
        return self.__base_directory

