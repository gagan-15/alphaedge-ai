"""
Zone Scoring Engine.

Sprint:
    2.34 - Zone Scoring Engine
"""

from backend.config.zone_scoring_config import (
    ZoneScoringConfig,
)
from backend.models.zone import Zone
from backend.models.zone_scoring.zone_score import (
    ZoneScore,
)
from backend.models.zone_scoring.zone_scoring_result import (
    ZoneScoringResult,
)
from backend.validators.zone_scoring_validator import (
    ZoneScoringValidator,
)


class ZoneScoringEngine:
    """
    Score demand and supply zones.
    """

    def __init__(
        self,
        config: ZoneScoringConfig | None = None,
    ) -> None:

        self._config = config or ZoneScoringConfig()

    def score(
        self,
        zones: list[Zone],
    ) -> ZoneScoringResult:
        """
        Score zones.
        """

        ZoneScoringValidator.validate(
            zones,
            self._config,
        )

        scored: list[ZoneScore] = []

        for zone in zones:

            freshness = self._config.freshness_weight if zone.is_fresh else 0.0

            strength = min(
                zone.strength,
                self._config.strength_weight,
            )

            touch = max(
                0.0,
                self._config.touch_weight - zone.touch_count,
            )

            merge_bonus = min(
                zone.merged_count,
                self._config.merge_bonus_weight,
            )

            total = freshness + strength + touch + merge_bonus

            scored.append(
                ZoneScore(
                    zone=zone,
                    freshness_score=freshness,
                    strength_score=strength,
                    touch_score=touch,
                    merge_bonus=merge_bonus,
                    total_score=min(
                        total,
                        self._config.maximum_score,
                    ),
                )
            )

        return ZoneScoringResult(
            scored_zones=scored,
        )
