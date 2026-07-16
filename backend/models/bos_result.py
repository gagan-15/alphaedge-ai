"""
AlphaEdge AI

Break of Structure Result Models

Sprint:
    2.29 - Break of Structure Engine

Version:
    v0.2.8
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from backend.models.swing_point import SwingPoint


class BOSDirection(str, Enum):
    """
    Break Of Structure direction.
    """

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


@dataclass(frozen=True)
class BOSEvent:
    """
    Represents one confirmed
    Break Of Structure event.
    """

    direction: BOSDirection

    break_index: int

    break_price: float

    broken_swing: SwingPoint

    break_distance: float

    break_distance_percentage: float

    confirmation_source: str

    is_confirmed: bool

    explanation: str


@dataclass(frozen=True)
class BOSResult:
    """
    Result returned by the
    Break Of Structure Engine.
    """

    events: list[BOSEvent] = field(default_factory=list)

    swings_evaluated: int = 0

    bullish_events: int = 0

    bearish_events: int = 0

    latest_bullish_event: Optional[BOSEvent] = None

    latest_bearish_event: Optional[BOSEvent] = None

    @property
    def latest_event(self) -> Optional[BOSEvent]:

        if not self.events:
            return None

        return self.events[-1]

    @property
    def has_bos(self) -> bool:

        return len(self.events) > 0

    @property
    def has_bullish_bos(self) -> bool:

        return self.bullish_events > 0

    @property
    def has_bearish_bos(self) -> bool:

        return self.bearish_events > 0