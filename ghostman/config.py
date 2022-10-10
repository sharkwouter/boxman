import os.path
from configparser import ConfigParser, SectionProxy, RawConfigParser
from typing import Dict, List

from ghostman.data.config.options import Options
from ghostman.data.config.repository import Repository


class Config:
    options: Options
    repositories: List[Repository]
    __base_directory: str
    __application_name: str

    def __init__(self, base_directory: str, application_name: str):
        self.__base_directory = base_directory
        self.__application_name = application_name

        self.__parse_config()

    def __parse_config(self):
        parser = ConfigParser(allow_no_value=True, comment_prefixes=['#'], )
        parser.read(
            [
                os.path.join(self.base_directory, "etc", f"{self.application_name}.conf"),
                os.path.join(self.base_directory, "etc", f"pacman.conf"),
            ],
            encoding='utf-8'
        )

        self.repositories = []
        for section in parser.sections():
            if section == "options":
                self.__parse_config_options(parser["options"])
            else:
                self.__parse_config_repository(parser[section])

    def __parse_config_options(self, options_section: SectionProxy):
        root_dir = options_section.get("RootDir", self.base_directory)
        cache_dir = options_section.get(
            "CacheDir",
            os.path.join(self.base_directory, "var", "cache", self.application_name, "pkg")
        )
        db_path = options_section.get(
            "DBPath",
            os.path.join(self.base_directory, "var", "lib", self.application_name)
        )
        self.options = Options(
            root_dir=root_dir,
            cache_dir=cache_dir,
            db_path=db_path
        )

    def __parse_config_repository(self, section: SectionProxy):
        self.repositories.append(Repository(section.name, section.get("Server")))

    @property
    def base_directory(self):
        return self.__base_directory

    @property
    def application_name(self):
        return self.__application_name
