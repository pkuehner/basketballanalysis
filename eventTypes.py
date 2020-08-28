from enum import Enum


class eventTypes(Enum):
    SHOT = "SHOT"
    REBOUND = "REBOUND"
    TEAM_REBOUND = "TEAM REBOUND"
    DEFENSE = "DEFENSE"
    TIMEOUT = "TIMEOUT"
    TURNOVER = "TURNOVER"
    TEAM_TURNOVER = "TEAM TURNOVER"
    FOUL = "FOUL"
    FREE_THROW = "FREE THROW"
    SUB = "SUB"
    JUMP = "JUMP BALL"
    VIOLATION = "VIOLATION"
    BLK = "BLOCK"
    STL = "STEAL"
    ERROR = "ERROR"

