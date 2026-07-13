"""
Pattern model for AlphaEdge AI.

Sprint:
    2.26 - Zone Detection Engine
"""

from dataclasses import dataclass
from enum import Enum


class PatternType(Enum):
    """
    Supported Demand & Supply patterns.
    """

    DROP_BASE_RALLY = "DROP_BASE_RALLY"

    RALLY_BASE_DROP = "RALLY_BASE_DROP"

    RALLY_BASE_RALLY = "RALLY_BASE_RALLY"

    DROP_BASE_DROP = "DROP_BASE_DROP"


@dataclass(frozen=True)
class Pattern:
    """
    Represents a detected Demand/Supply pattern.
    """

    pattern_type: PatternType
