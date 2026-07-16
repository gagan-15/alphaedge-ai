"""
Zone Rank model.

Sprint:
    2.35 - Zone Ranking Engine
"""

from dataclasses import dataclass

from backend.models.zone_scoring.zone_score import ZoneScore


@dataclass(frozen=True)
class ZoneRank:
    """
    Represents a ranked zone.
    """

    zone_score: ZoneScore

    rank: int
