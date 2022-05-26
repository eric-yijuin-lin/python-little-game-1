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
    SwapingForward = 2
    SwapingBack = 3,
    ShowingMatched = 4,
    ClearingBlock = 5,
    ClearingAnimation = 6,
    ReAligningBlock = 7,
    DropingNewBlock = 8