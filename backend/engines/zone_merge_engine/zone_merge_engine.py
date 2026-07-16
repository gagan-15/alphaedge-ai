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
from backend.models.zone_merge.zone_merge_result import (
    ZoneMergeResult,
)
from backend.validators.zone_merge_validator import (
    ZoneMergeValidator,
)


class ZoneMergeEngine:
    """
    Merge overlapping demand and supply zones.
    """

    def __init__(
        self,
        config: ZoneMergeConfig | None = None,
    ) -> None:

        self._config = config or ZoneMergeConfig()

    def merge(
        self,
        zones: list[Zone],
    ) -> ZoneMergeResult:
        """
        Merge compatible zones.
        """

        ZoneMergeValidator.validate(
            zones,
            self._config,
        )

        merged: list[MergedZone] = []

        visited: set[int] = set()

        for i, zone in enumerate(zones):

            if i in visited:
                continue

            current = zone

            originals = [zone]

            for j in range(
                i + 1,
                len(zones),
            ):

                if j in visited:
                    continue

                candidate = zones[j]

                if not self._can_merge(
                    current,
                    candidate,
                ):
                    continue

                current = self._merge_zone(
                    current,
                    candidate,
                )

                originals.append(
                    candidate,
                )

                visited.add(j)

            merged.append(
                MergedZone(
                    zone=current,
                    original_zones=originals,
                )
            )

        return ZoneMergeResult(
            merged_zones=merged,
            original_zone_count=len(zones),
            merged_zone_count=len(merged),
        )

    def _can_merge(
        self,
        zone1: Zone,
        zone2: Zone,
    ) -> bool:
        """
        Return True if two zones
        can be merged.
        """

        if zone1.zone_type != zone2.zone_type:
            return False

        overlap = min(
            zone1.upper_price,
            zone2.upper_price,
        ) - max(
            zone1.lower_price,
            zone2.lower_price,
        )

        if overlap >= 0:
            return True

        if not self._config.merge_adjacent_zones:
            return False

        gap = abs(overlap)

        zone_height = max(
            zone1.upper_price - zone1.lower_price,
            zone2.upper_price - zone2.lower_price,
        )

        allowed_gap = zone_height * self._config.maximum_gap_percentage / 100

        return gap <= allowed_gap

    def _merge_zone(
        self,
        zone1: Zone,
        zone2: Zone,
    ) -> Zone:
        """
        Merge two compatible zones.
        """

        return Zone(
            zone_type=zone1.zone_type,
            upper_price=max(
                zone1.upper_price,
                zone2.upper_price,
            ),
            lower_price=min(
                zone1.lower_price,
                zone2.lower_price,
            ),
            created_index=min(
                zone1.created_index,
                zone2.created_index,
            ),
            strength=max(
                zone1.strength,
                zone2.strength,
            ),
            is_fresh=(zone1.is_fresh or zone2.is_fresh),
            touch_count=min(
                zone1.touch_count,
                zone2.touch_count,
            ),
            merged_count=(zone1.merged_count + zone2.merged_count),
        )
