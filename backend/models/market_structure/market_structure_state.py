"""
Market Structure State.

Sprint:
    2.30 - Market Structure Foundation
"""

from dataclasses import dataclass
from enum import Enum


class StructureTrend(str, Enum):
    """
    Overall market structure trend.
    """

    BULLISH = "BULLISH"

    BEARISH = "BEARISH"

    SIDEWAYS = "SIDEWAYS"


@dataclass(frozen=True)
class StructureState:
    """
    Current market structure state.
    """

    trend: StructureTrend

    last_higher_high: float | None = None

    last_higher_low: float | None = None

    last_lower_high: float | None = None

    last_lower_low: float | None = None
