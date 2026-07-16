"""
Zone Scoring Validator.

Sprint:
    2.34 - Zone Scoring Engine
"""

from backend.config.zone_scoring_config import (
    ZoneScoringConfig,
)
from backend.models.zone import Zone


class ZoneScoringValidator:
    """
    Validate Zone Scoring inputs.
    """

    @staticmethod
    def validate(
        zones: list[Zone],
        config: ZoneScoringConfig,
    ) -> None:

        if not zones:
            raise ValueError("zones cannot be empty.")

        weights = (
            config.freshness_weight
            + config.strength_weight
            + config.touch_weight
            + config.merge_bonus_weight
        )

        if weights != config.maximum_score:
            raise ValueError("Scoring weights must equal maximum_score.")
