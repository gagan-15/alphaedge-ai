"""
Zone Ranking Configuration.

Sprint:
    2.35 - Zone Ranking Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneRankingConfig:
    """
    Configuration for Zone Ranking Engine.
    """

    descending: bool = True

    maximum_ranked_zones: int | None = None

    prioritize_fresh_zones: bool = True
