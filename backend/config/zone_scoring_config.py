"""
Zone Scoring Configuration.

Sprint:
    2.34 - Zone Scoring Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneScoringConfig:
    """
    Configuration for Zone Scoring Engine.
    """

    base_quality_weight: float = 15.0
    departure_quality_weight: float = 30.0
    legout_dominance_weight: float = 15.0
    structural_clearance_weight: float = 15.0
    lifecycle_quality_weight: float = 15.0
    authenticity_quality_weight: float = 10.0

    maximum_score: float = 100.0

    # Compatibility aliases for older API consumers. New methodology does not
    # use the former touch/merge model.
    @property
    def freshness_weight(self) -> float:
        return self.lifecycle_quality_weight

    @property
    def strength_weight(self) -> float:
        return self.departure_quality_weight

    @property
    def touch_weight(self) -> float:
        return 0.0

    @property
    def merge_bonus_weight(self) -> float:
        return 0.0
