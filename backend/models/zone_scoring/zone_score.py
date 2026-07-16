"""
Zone Score model.

Sprint:
    2.34 - Zone Scoring Engine
"""

from dataclasses import dataclass

from backend.models.zone import Zone


@dataclass(frozen=True)
class ZoneScore:
    """
    Represents the score of a zone.
    """

    zone: Zone

    freshness_score: float

    strength_score: float

    touch_score: float

    merge_bonus: float

    total_score: float
