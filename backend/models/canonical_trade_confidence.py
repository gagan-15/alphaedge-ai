"""Immutable result models for AlphaEdge deterministic Trade Confidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TradeConfidenceLabel(str, Enum):
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    CONFLICTED = "CONFLICTED"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"


class ContextDataSufficiency(str, Enum):
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class CanonicalTradeConfidence:
    """User-facing contextual score composed from canonical outputs."""

    total_score: float
    label: TradeConfidenceLabel
    zone_quality_score: float
    zone_quality_contribution: float
    location_contribution: float
    trend_contribution: float
    location_alignment: str
    trend_alignment: str
    combined_context: str
    htf_overlap_type: str
    htf_direction_compatibility: str
    data_sufficiency: ContextDataSufficiency
    reason_codes: tuple[str, ...]
    evidence: tuple[str, ...]
