"""
Market Structure Point model.

Sprint:
    2.31 - Market Structure Engine
"""

from dataclasses import dataclass
from enum import Enum

from backend.models.swing_point import SwingPoint


class StructurePointType(str, Enum):
    """
    Supported market structure point types.
    """

    HIGHER_HIGH = "HIGHER_HIGH"
    HIGHER_LOW = "HIGHER_LOW"
    LOWER_HIGH = "LOWER_HIGH"
    LOWER_LOW = "LOWER_LOW"
    EQUAL_HIGH = "EQUAL_HIGH"
    EQUAL_LOW = "EQUAL_LOW"


@dataclass(frozen=True)
class StructurePoint:
    """
    Represents a classified market structure point.
    """

    swing: SwingPoint

    point_type: StructurePointType

    previous_swing: SwingPoint | None = None

    @property
    def price(self) -> float:
        """
        Structure point price.
        """

        return self.swing.price

    @property
    def index(self) -> int:
        """
        Structure point index.
        """

        return self.swing.index
