import os

import __main__

from boxman.config import Config
from boxman.args_parser import parse_args
from boxman.boxman import Boxman


def run():
    base_directory = os.path.dirname(os.path.dirname(__main__.__file__))
    config = Config(base_directory)
    args = parse_args()
    boxman = Boxman(config)
    boxman.run(args)


if __name__ == "__main__":
    raise Exception(
        "Please call run from the binary, otherwise the install path will be off"
    )
