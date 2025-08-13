from enum import Enum


class ScopesEnum(str, Enum):
    Overview = "Overview"
    Player = "Player"
    Round = "Round"

class ViewEnum(str, Enum):
    Popularity = "Popularity"
    Transactions = "Transactions"