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
            config.base_quality_weight
            + config.departure_quality_weight
            + config.legout_dominance_weight
            + config.structural_clearance_weight
            + config.lifecycle_quality_weight
            + config.authenticity_quality_weight
        )

        if weights != config.maximum_score:
            raise ValueError("Scoring weights must equal maximum_score.")
