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
    ShowingFirstMatched = 4,
    ClearingFirstMatched = 5,
    AnimatingFirstClear = 6,
    ReAligningBlock = 7,
    AnimatingReAlign = 8,
    NewBlockCreating = 9,
    DroppedBlockMatching = 10,
    ShowingDroppedMatch = 11,
    ClearingDroppedMatch = 12,
    AnimatingDroppedClear = 13,
    ShowTurnScore = 99