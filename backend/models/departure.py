from dataclasses import dataclass
from enum import Enum


class DepartureDirection(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


@dataclass(frozen=True)
class Departure:
    direction: DepartureDirection
    departure_index: int
