"""
Zone Merge Validator.

Sprint:
    2.33 - Zone Merge Engine
"""

from backend.config.zone_merge_config import (
    ZoneMergeConfig,
)
from backend.models.zone import Zone


class ZoneMergeValidator:
    """
    Validate Zone Merge inputs.
    """

    @staticmethod
    def validate(
        zones: list[Zone],
        config: ZoneMergeConfig,
    ) -> None:

        if not zones:
            raise ValueError("zones cannot be empty.")

        if config.overlap_percentage < 0 or config.overlap_percentage > 100:
            raise ValueError("overlap_percentage must be between 0 and 100.")

        if config.maximum_gap_percentage < 0:
            raise ValueError("maximum_gap_percentage cannot be negative.")
