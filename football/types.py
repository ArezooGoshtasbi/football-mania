from enum import Enum

class PredictionStatus(Enum):
    HOME = "Home Win"
    AWAY = "Away Win"
    DRAW = "Draw"


class TaskStatus(Enum):
    SCHEDULED = "scheduled"
    FINISHED = "finished"
