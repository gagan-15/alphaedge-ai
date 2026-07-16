"""
Zone Merge Engine.

Sprint:
    2.33 - Zone Merge Engine
"""

from backend.config.zone_merge_config import (
    ZoneMergeConfig,
)
from backend.models.zone import Zone
from backend.models.zone_merge.merged_zone import (
    MergedZone,
)
from backend.validators.zone_merge_validator import (
    ZoneMergeValidator,
)


class ZoneMergeEngine:
    """
    Merge overlapping demand/supply zones.
    """

    def __init__(
        self,
        config: ZoneMergeConfig | None = None,
    ) -> None:

        self._config = config or ZoneMergeConfig()

    def merge(
        self,
        zones: list[Zone],
    ) -> list[MergedZone]:
        """
        Merge zones.
        """

        ZoneMergeValidator.validate(
            zones,
            self._config,
        )

        return [
            MergedZone(
                zone=zone,
                merged_count=1,
                confidence=1.0,
            )
            for zone in zones
        ]
