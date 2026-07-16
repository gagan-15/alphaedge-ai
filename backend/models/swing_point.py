"""
AlphaEdge AI

Swing Point Model

Sprint : 2.29
Version: v0.2.8
"""

from dataclasses import dataclass
from enum import Enum


class SwingType(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


@dataclass(frozen=True)
class SwingPoint:
    """
    Represents a confirmed market swing.
    """

    index: int
    price: float
    swing_type: SwingType
    confirmation_index: int

    @property
    def is_high(self) -> bool:
        return self.swing_type == SwingType.HIGH

    @property
    def is_low(self) -> bool:
        return self.swing_type == SwingType.LOW