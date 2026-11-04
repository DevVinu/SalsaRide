from enum import Enum


class Direction(str, Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"


class SignalPhase(str, Enum):
    NORTH_SOUTH_GREEN = "NORTH_SOUTH_GREEN"
    NORTH_SOUTH_YELLOW = "NORTH_SOUTH_YELLOW"
    ALL_RED_TRANSITION_1 = "ALL_RED_TRANSITION_1"
    EAST_WEST_GREEN = "EAST_WEST_GREEN"
    EAST_WEST_YELLOW = "EAST_WEST_YELLOW"
    ALL_RED_TRANSITION_2 = "ALL_RED_TRANSITION_2"


class SignalLamp(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class CongestionLevel(str, Enum):
    CLEAR = "CLEAR"
    MODERATE = "MODERATE"
    OVERCROWDED = "OVERCROWDED"


class UserRole(str, Enum):
    DRIVER = "DRIVER"
    ADMINISTRATOR = "ADMINISTRATOR"
    EMERGENCY_RESPONDER = "EMERGENCY_RESPONDER"

