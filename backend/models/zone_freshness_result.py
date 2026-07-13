"""
Zone Freshness Result model for AlphaEdge AI.

Sprint:
    2.27 - Zone Freshness Engine
"""

from dataclasses import dataclass
from enum import Enum


class FreshnessStatus(Enum):
    """
    Supported freshness states.
    """

    FRESH = "FRESH"
    TESTED = "TESTED"
    WEAK = "WEAK"
    BROKEN = "BROKEN"


@dataclass(frozen=True)
class ZoneFreshnessResult:
    """
    Result returned by the Zone Freshness Engine.
    """

    status: FreshnessStatus
    touch_count: int
    penetration_percent: float
    is_broken: bool
