"""
Zone Strength Result model.

Sprint:
    2.28 - Zone Strength Engine
"""

from dataclasses import dataclass
from enum import Enum


class StrengthStatus(Enum):
    """
    Overall zone strength.
    """

    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


@dataclass(frozen=True)
class ZoneStrengthResult:
    """
    Result produced by the Zone Strength Engine.
    """

    status: StrengthStatus

    departure_distance: float

    departure_candle_count: int

    departure_speed: float

    volume_confirmed: bool

    gap_present: bool
