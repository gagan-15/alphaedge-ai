"""
Zone Score model.

Sprint:
    2.34 - Zone Scoring Engine
"""

from dataclasses import dataclass

from backend.models.zone import Zone
from backend.models.zone_scoring.canonical_zone_quality import ZoneQualityComponent


@dataclass(frozen=True)
class ZoneScore:
    """
    Represents the score of a zone.
    """

    zone: Zone

    freshness_score: float

    strength_score: float

    touch_score: float

    merge_bonus: float

    total_score: float

    raw_score: float = 0.0

    quality_cap: float = 100.0

    label: str = "WEAK"

    components: tuple[ZoneQualityComponent, ...] = ()

    reason_codes: tuple[str, ...] = ()

    evidence_summary: tuple[str, ...] = ()

    base_quality_score: float = 0.0

    departure_quality_score: float = 0.0

    legout_dominance_score: float = 0.0

    structural_clearance_score: float = 0.0

    lifecycle_quality_score: float = 0.0

    authenticity_quality_score: float = 0.0
