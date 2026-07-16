"""
Zone Merge Result.

Sprint:
    2.33 - Zone Merge Engine
"""

from dataclasses import dataclass, field

from backend.models.zone_merge.merged_zone import (
    MergedZone,
)


@dataclass(frozen=True)
class ZoneMergeResult:
    """
    Result returned by
    Zone Merge Engine.
    """

    merged_zones: list[MergedZone] = field(
        default_factory=list,
    )

    original_zone_count: int = 0

    merged_zone_count: int = 0

    @property
    def has_merges(
        self,
    ) -> bool:
        """
        Return True if
        any zones were merged.
        """

        return self.original_zone_count > self.merged_zone_count

    @property
    def total_saved_zones(
        self,
    ) -> int:
        """
        Number of zones eliminated
        by merging.
        """

        return self.original_zone_count - self.merged_zone_count

    @property
    def merge_ratio(
        self,
    ) -> float:
        """
        Merge efficiency ratio.
        """

        if self.original_zone_count == 0:
            return 0.0

        return self.total_saved_zones / self.original_zone_count
