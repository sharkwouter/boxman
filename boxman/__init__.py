import os

import __main__

from boxman.config import Config
from boxman.args_parser import parse_args
from boxman.boxman import Boxman
from boxman.database_manager import DatabaseManager


def run():
    base_directory = os.path.dirname(os.path.dirname(__main__.__file__))
    config = Config(base_directory)

    database_manager = DatabaseManager(config)

    args = parse_args()
    boxman = Boxman(config, database_manager)
    boxman.run(args)


if __name__ == "__main__":
    raise Exception(
        "Please call run from the binary, otherwise the install path will be off"
    )
