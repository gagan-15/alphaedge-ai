"""
Zone model for AlphaEdge AI.

Represents a Demand or Supply zone.

Sprint:
    2.25 - Demand & Supply Foundation
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
    zone_type: ZoneType
    upper_price: float
    lower_price: float
    created_index: int
