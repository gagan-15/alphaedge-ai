"""
Zone Ranking Result.

Sprint:
    2.35 - Zone Ranking Engine
"""

from dataclasses import dataclass, field

from backend.models.zone_ranking.zone_rank import (
    ZoneRank,
)


@dataclass(frozen=True)
class ZoneRankingResult:
    """
    Result returned by
    Zone Ranking Engine.
    """

    ranked_zones: list[ZoneRank] = field(
        default_factory=list,
    )

    @property
    def best_zone(
        self,
    ) -> ZoneRank | None:
        """
        Return the highest ranked zone.
        """

        if not self.ranked_zones:
            return None

        return self.ranked_zones[0]
