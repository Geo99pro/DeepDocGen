from enum import Enum, Flag, auto


class Align(Enum):
    TOP = auto(),
    BOTTOM = auto(),
    CENTER = auto(),
    LEFT = auto(),
    RIGHT = auto()

class FigureType(Enum):
    BACKGROUND = auto(),
    EQUATIONS = auto(),
    FIGURES = auto(),
    GRAPHS = auto(),
    LOGOS = auto(),
    TABLES = auto()

class Subtypes(Enum):
    IMAGE = 1,
    PARAGRAPH = 2,
    TEXT = 2,
    TITLE = 4,
    SUBTITLE = 8,
    SUBSUBTITLE = 16,
    TITLE_TYPES = 28,
    LIST = 32,
    PAGENUMBER = 64,
    TABLE = 128,
    EQUATION = 256,
    TABLE_CAPTION = 512,
    IMAGE_CAPTION = 1024
