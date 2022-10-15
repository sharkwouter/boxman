from enum import Enum, auto


class Mode(Enum):
    INSTALL = auto()
    LIST = auto()
    SEARCH = auto()
    INSTALLED = auto()
    REMOVE = auto()
    SHOW = auto()
    UPDATE = auto()
    NOT_SET = auto()
