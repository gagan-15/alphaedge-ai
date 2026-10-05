from dataclasses import dataclass
from enum import Enum


class DepartureDirection(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class DepartureStrength(Enum):
    WEAK = "WEAK"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


@dataclass(frozen=True)
class Departure:
    direction: DepartureDirection
    departure_index: int
    end_index: int | None = None
    strength: DepartureStrength | None = None
    leg_in_direction: DepartureDirection | None = None
    leg_in_start_index: int | None = None
    leg_in_end_index: int | None = None
    significant_gap: bool = False
    good_closing: bool = False
    gap_measurement: float | None = None
    closing_comparison_reference: float | None = None
    qualifying_close: float | None = None
    acceptance_reason: str | None = None
