"""
Change of Character Detector.

Sprint:
    2.30 - Change of Character Engine
"""

from backend.models.bos_result import BOSEvent, BOSDirection
from backend.models.structure_trend import StructureTrend


class CHoCHDetector:
    """
    Detect Change of Character events from
    confirmed BOS events and current trend.
    """

    def detect(
        self,
        trend: StructureTrend,
        bos_events: list[BOSEvent],
    ) -> list[BOSEvent]:
        """
        Detect CHoCH events.
        """

        choch_events: list[BOSEvent] = []

        for event in bos_events:

            if (
                trend == StructureTrend.BEARISH
                and event.direction == BOSDirection.BULLISH
            ):
                choch_events.append(event)

            elif (
                trend == StructureTrend.BULLISH
                and event.direction == BOSDirection.BEARISH
            ):
                choch_events.append(event)

        return choch_events
