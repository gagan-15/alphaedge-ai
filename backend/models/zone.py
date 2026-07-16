"""
Zone model for AlphaEdge AI.

Represents a Demand or Supply zone.

Sprint:
    2.33 - Zone Merge Engine
"""

from dataclasses import dataclass
from enum import Enum


class ZoneType(Enum):
    """
    Supported zone types.
    """

    DEMAND = "DEMAND"
    SUPPLY = "SUPPLY"


@dataclass(frozen=True)
class Zone:
    """
    Canonical Demand/Supply zone.
    """

    zone_type: ZoneType

    upper_price: float

    lower_price: float

    created_index: int

    strength: float = 0.0

    is_fresh: bool = True

    touch_count: int = 0

    merged_count: int = 1
