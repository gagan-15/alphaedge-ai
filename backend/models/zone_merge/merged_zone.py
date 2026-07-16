"""
Merged Zone model.

Sprint:
    2.33 - Zone Merge Engine
"""

from dataclasses import dataclass, field

from backend.models.zone import Zone


@dataclass(frozen=True)
class MergedZone:
    """
    Represents a merged demand/supply zone.
    """

    zone: Zone

    original_zones: list[Zone] = field(
        default_factory=list,
    )

    @property
    def merged_count(
        self,
    ) -> int:
        """
        Return merged zone count.
        """

        return len(
            self.original_zones,
        )

    @property
    def confidence(
        self,
    ) -> float:
        """
        Confidence derived from
        merged zone count.
        """

        return min(
            1.0,
            self.merged_count / 5,
        )
