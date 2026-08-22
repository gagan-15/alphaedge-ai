"""
Zone model for AlphaEdge AI.

Represents a Demand or Supply zone.

Sprint:
    2.33 - Zone Merge Engine
"""

from dataclasses import dataclass
from enum import Enum

from backend.models.zone_boundary import ZoneBoundaryResult
from backend.models.formation_evidence import CanonicalFormationEvidence


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

    pattern_type: str | None = None

    boundary_result: ZoneBoundaryResult | None = None

    formation_evidence: CanonicalFormationEvidence | None = None
