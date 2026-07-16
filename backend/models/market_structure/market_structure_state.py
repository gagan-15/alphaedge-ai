"""
Market Structure State.

Sprint:
    2.31 - Market Structure Engine
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

    @property
    def is_bullish(self) -> bool:
        """
        Return True if trend is bullish.
        """

        return self.trend == StructureTrend.BULLISH

    @property
    def is_bearish(self) -> bool:
        """
        Return True if trend is bearish.
        """

        return self.trend == StructureTrend.BEARISH

    @property
    def is_sideways(self) -> bool:
        """
        Return True if trend is sideways.
        """

        return self.trend == StructureTrend.SIDEWAYS
