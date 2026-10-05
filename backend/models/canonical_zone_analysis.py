"""Immutable read model composed exclusively from canonical engine outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.models.formation_evidence import CanonicalFormationEvidence


@dataclass(frozen=True)
class CanonicalZoneAnalysis:
    """One deterministic source for future downstream decision engines.

    This model owns no methodology. Every field is an existing canonical
    engine result preserved without recomputation.
    """

    zone_id: str
    symbol: str
    timeframe: str
    zone_type: str
    pattern: str | None
    proximal: float
    distal: float
    formation_evidence: CanonicalFormationEvidence | None
    lifecycle: Any
    authenticity: Any
    zone_quality: Any
    canonical_trend: Any
    htf_context: Any
    alignment: str
    significant_gap: bool
    gap_measurement: float | None
    trend_timeframe: str | None = None
    location_timeframe: str | None = None
    trend_alignment: str = "UNKNOWN"
    location_relationship: str = "NO_OVERLAP"
    location_compatibility: str = "NO_HTF_CONTEXT"
    combined_context: Any = None
    data_sufficient: bool = False
    reason_codes: tuple[str, ...] = ()
