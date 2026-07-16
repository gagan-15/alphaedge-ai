"""
Zone Scoring Result.

Sprint:
    2.34 - Zone Scoring Engine
"""

from dataclasses import dataclass, field

from backend.models.zone_scoring.zone_score import (
    ZoneScore,
)


@dataclass(frozen=True)
class ZoneScoringResult:
    """
    Result returned by
    Zone Scoring Engine.
    """

    scored_zones: list[ZoneScore] = field(
        default_factory=list,
    )

    @property
    def highest_score(
        self,
    ) -> float:

        if not self.scored_zones:
            return 0.0

        return max(zone.total_score for zone in self.scored_zones)
