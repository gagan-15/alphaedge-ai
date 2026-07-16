"""
Structure Trend model.

Sprint:
    2.30 - Change of Character Engine
"""

from enum import Enum


class StructureTrend(Enum):
    """
    Market structure trend.
    """

    BULLISH = "bullish"

    BEARISH = "bearish"

    SIDEWAYS = "sideways"
