"""
Zone Ranking Engine.

Sprint:
    2.35 - Zone Ranking Engine
"""

from backend.config.zone_ranking_config import (
    ZoneRankingConfig,
)
from backend.models.zone_ranking.zone_rank import (
    ZoneRank,
)
from backend.models.zone_ranking.zone_ranking_result import (
    ZoneRankingResult,
)
from backend.models.zone_scoring.zone_score import (
    ZoneScore,
)
from backend.validators.zone_ranking_validator import (
    ZoneRankingValidator,
)


class ZoneRankingEngine:
    """
    Rank scored demand and supply zones.
    """

    def __init__(
        self,
        config: ZoneRankingConfig | None = None,
    ) -> None:

        self._config = config or ZoneRankingConfig()

    def rank(
        self,
        scored_zones: list[ZoneScore],
    ) -> ZoneRankingResult:
        """
        Rank scored zones.
        """

        ZoneRankingValidator.validate(
            scored_zones,
            self._config,
        )

        ordered = sorted(
            scored_zones,
            key=lambda zone: zone.total_score,
            reverse=self._config.descending,
        )

        if self._config.maximum_ranked_zones is not None:
            ordered = ordered[: self._config.maximum_ranked_zones]

        ranked = [
            ZoneRank(
                zone_score=zone,
                rank=index + 1,
            )
            for index, zone in enumerate(
                ordered,
            )
        ]

        return ZoneRankingResult(
            ranked_zones=ranked,
        )
