import os.path
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class Repository:
    name: str
    server: str

    @property
    def database_url(self) -> str:
        return urljoin(f"{self.server}/", f"{self.name}.db")

    def get_database_path(self, db_path: str) -> str:
        return os.path.join(db_path, f"{self.name}.db")
