"""
Zone Ranking Validator.

Sprint:
    2.35 - Zone Ranking Engine
"""

from backend.config.zone_ranking_config import (
    ZoneRankingConfig,
)
from backend.models.zone_scoring.zone_score import (
    ZoneScore,
)


class ZoneRankingValidator:
    """
    Validate Zone Ranking inputs.
    """

    @staticmethod
    def validate(
        scored_zones: list[ZoneScore],
        config: ZoneRankingConfig,
    ) -> None:

        if not scored_zones:
            raise ValueError("scored_zones cannot be empty.")

        if config.maximum_ranked_zones is not None and config.maximum_ranked_zones < 1:
            raise ValueError("maximum_ranked_zones must be greater than zero.")
