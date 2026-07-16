"""
Structure Trend Resolver.

Sprint:
    2.30 - Change of Character Engine
"""

from backend.models.structure_trend import StructureTrend
from backend.models.swing_point import SwingPoint, SwingType


class StructureTrendResolver:
    """
    Resolve the current market structure trend
    from confirmed swing points.
    """

    def resolve(
        self,
        swings: list[SwingPoint],
    ) -> StructureTrend:
        """
        Determine the current trend.
        """

        highs = [swing for swing in swings if swing.swing_type == SwingType.HIGH]

        lows = [swing for swing in swings if swing.swing_type == SwingType.LOW]

        if len(highs) < 2 or len(lows) < 2:
            return StructureTrend.SIDEWAYS

        latest_high = highs[-1].price
        previous_high = highs[-2].price

        latest_low = lows[-1].price
        previous_low = lows[-2].price

        if latest_high > previous_high and latest_low > previous_low:
            return StructureTrend.BULLISH

        if latest_high < previous_high and latest_low < previous_low:
            return StructureTrend.BEARISH

        return StructureTrend.SIDEWAYS
