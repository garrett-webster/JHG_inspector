from enum import Enum

class ScopesEnum(str, Enum):
    Overview = "Overview"
    Player = "Player"
    Round = "Round"

class ToolPageEnum(str, Enum):
    Popularity = "Popularity"