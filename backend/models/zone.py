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
    """
    Represents a price zone.

    Attributes:
        zone_type:
            Demand or Supply.

        upper_price:
            Upper boundary of the zone.

        lower_price:
            Lower boundary of the zone.
    """

    zone_type: ZoneType
    upper_price: float
    lower_price: float