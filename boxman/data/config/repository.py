from dataclasses import dataclass


@dataclass
class Repository:
    name: str
    server: str

    @property
    def database_url(self):
        return f"{self.server}/{self.name}.db"
