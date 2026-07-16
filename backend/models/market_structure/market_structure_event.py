"""
Market Structure Event.

Sprint:
    2.31 - Market Structure Engine
"""

from dataclasses import dataclass
from enum import Enum

from backend.models.market_structure.market_structure_point import (
    StructurePoint,
)


class StructureEventType(str, Enum):
    """
    Supported market structure events.
    """

    BOS = "BOS"

    CHOCH = "CHOCH"

    CONTINUATION = "CONTINUATION"

    REVERSAL = "REVERSAL"


@dataclass(frozen=True)
class StructureEvent:
    """
    Represents a market structure event.
    """

    event_type: StructureEventType

    structure_point: StructurePoint

    price: float

    candle_index: int

    explanation: str

    @property
    def index(self) -> int:
        """
        Return event candle index.
        """

        return self.candle_index
