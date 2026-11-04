from enum import IntEnum

class CellType(IntEnum):
    EMPTY = 0
    FOOD = 1
    WALL = 2
    AGENT = 3