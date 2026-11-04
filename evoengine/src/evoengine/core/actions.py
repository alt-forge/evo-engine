from enum import IntEnum

class Action(IntEnum): # Класс действий
    STAY = 0
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

    @classmethod
    def size(cls) -> int:
        return len(cls)

ACTION_DELTAS = { # Направления
    Action.STAY:  (0, 0),
    Action.RIGHT: (1, 0),
    Action.LEFT:  (-1, 0),
    Action.UP:    (0, 1),
    Action.DOWN:  (0, -1),
}