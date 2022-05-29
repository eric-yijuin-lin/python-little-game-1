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
    WaitingStart = 1,
    Idle = 2,
    SwapingForward = 3,
    SwapingBack = 4,
    ShowingFirstMatched = 5,
    ClearingFirstMatched = 6,
    AnimatingFirstClear = 7,
    ReAligningBlock = 8,
    AnimatingReAlign = 9,
    NewBlockCreating = 10,
    DroppedBlockMatching = 11,
    ShowingDroppedMatch = 12,
    ClearingDroppedMatch = 13,
    AnimatingDroppedClear = 14,
    ShowTurnScore = 99