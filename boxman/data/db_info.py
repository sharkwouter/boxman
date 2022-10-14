from dataclasses import dataclass


@dataclass
class DbInfo:
    name: str
    path: str
    url: str
