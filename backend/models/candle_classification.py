"""Canonical, deterministic candle-classification evidence."""

from dataclasses import dataclass
from enum import Enum


class CandleDirection(Enum):
    """Direction determined only from open and close."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class CandleStructure(Enum):
    """GTF body-to-range structural classification."""

    BASE = "BASE"
    BOUNDARY = "BOUNDARY"
    EXCITING = "EXCITING"


@dataclass(frozen=True)
class CandleClassification:
    """Auditable result for one validated OHLC candle."""

    index: int
    direction: CandleDirection
    structure: CandleStructure
    body: float
    candle_range: float
    body_ratio: float
    explosive: bool
    range_to_median: float | None = None
    close_location: float | None = None
