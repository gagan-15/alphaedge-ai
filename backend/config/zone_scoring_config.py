"""
Zone Scoring Configuration.

Sprint:
    2.34 - Zone Scoring Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneScoringConfig:
    """
    Configuration for Zone Scoring Engine.
    """

    freshness_weight: float = 30.0

    strength_weight: float = 35.0

    touch_weight: float = 20.0

    merge_bonus_weight: float = 15.0

    maximum_score: float = 100.0
