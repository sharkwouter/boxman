from enum import Enum, auto


class Mode(Enum):
    INSTALL = auto()
    LIST = auto()
    SEARCH = auto()
    INSTALLED = auto()
    FILES = auto()
    REMOVE = auto()
    SHOW = auto()
    UPDATE = auto()
    CONFIG = auto()
    NOT_SET = auto()
