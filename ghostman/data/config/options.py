from dataclasses import dataclass


@dataclass
class Options:
    root_dir: str
    db_path: str
    cache_dir: str
