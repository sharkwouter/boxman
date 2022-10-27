import os.path
from urllib.parse import urljoin


class Repository:
    __name: str
    __url: str
    __path: str

    def __init__(self, name, server, db_path):
        self.__name = name
        self.__url = urljoin(f"{server}/", f"{name}.db")
        self.__path = os.path.join(db_path, f"{name}.db")

    @property
    def name(self) -> str:
        return self.__name

    @property
    def url(self) -> str:
        return self.__url

    @property
    def path(self) -> str:
        return self.__path

    @property
    def dir(self) -> str:
        return os.path.dirname(self.__path)
