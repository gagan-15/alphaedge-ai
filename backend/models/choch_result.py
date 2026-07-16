"""
Change of Character (CHoCH) Result.

Sprint:
    2.30 - Change of Character Engine
"""

from dataclasses import dataclass

from backend.models.bos_result import BOSEvent


@dataclass(slots=True)
class CHoCHResult:
    """
    Result returned by the CHoCH Engine.
    """

    has_choch: bool

    has_bullish_choch: bool

    has_bearish_choch: bool

    latest_event: BOSEvent | None

    latest_bullish_event: BOSEvent | None

    latest_bearish_event: BOSEvent | None

    bullish_events: int

    bearish_events: int

    total_events: int

    swings_evaluated: int
