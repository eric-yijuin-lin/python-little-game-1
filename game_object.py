from enum import Enum

class CellObject:
    x: int
    y: int
    color: str
    def __init__(self, x, y, color) -> None:
        self.x = x
        self.y = y
        self.color = color

class GameStatus(Enum):
    Initializing = 0,
    Idle = 1,
    SwapForward = 2
    SwapingBack = 3,
    ShowingMatched = 4,
    ClearingCell = 5,
    ReAligningCell = 6,
    DropingNewCell = 7