"""
Zone Quality model.

Sprint:
    2.67 - Zone Quality Scoring
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneQuality:
    """
    Represents the quality metrics
    of a detected zone.
    """

    base_score: float

    leg_in_score: float

    leg_out_score: float

    freshness_score: float

    total_score: float
