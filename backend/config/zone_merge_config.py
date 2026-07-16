"""
Zone Merge Configuration.

Sprint:
    2.33 - Zone Merge Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneMergeConfig:
    """
    Configuration for Zone Merge Engine.
    """

    overlap_percentage: float = 50.0

    merge_adjacent_zones: bool = True

    maximum_gap_percentage: float = 0.25

    preserve_strongest_zone: bool = True

    preserve_freshest_zone: bool = True

    enable_logging: bool = True
