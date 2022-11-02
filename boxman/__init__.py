import os

from boxman.config import Config
from boxman.args_parser import parse_args
from boxman.boxman import Boxman
from boxman.local_database import LocalDatabase
from boxman.database_manager import DatabaseManager


def run():
    config = Config()
    local_database = LocalDatabase(config)
    database_manager = DatabaseManager(local_database, config)

    args = parse_args()
    boxman = Boxman(config, database_manager)
    boxman.run(args)


if __name__ == "__main__":
    run()
