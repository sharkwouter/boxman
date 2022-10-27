import os.path
from urllib.parse import urljoin


class Repository:
    __name: str
    __url: str
    __path: str
    __dir: str

    def __init__(self, name: str, server: str, db_path: str):
        self.__name = name
        self.__dir = os.path.join(db_path, "sync")

        if not server.endswith("/"):
            server += "/"

        self.__url = urljoin(server, f"{name}.db")
        self.__path = os.path.join(self.__dir, f"{name}.db")

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
        return self.__dir
