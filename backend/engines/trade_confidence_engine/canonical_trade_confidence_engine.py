"""AlphaEdge deterministic Trade Confidence normalization.

This engine is informational only. It consumes canonical outputs and owns no
formation, lifecycle, authenticity, quality, HTF, or trend methodology.
"""

from __future__ import annotations

from typing import Any

from backend.models.canonical_trade_confidence import (
    CanonicalTradeConfidence,
    ContextDataSufficiency,
    TradeConfidenceLabel,
)
from backend.models.canonical_zone_analysis import CanonicalZoneAnalysis


class CanonicalTradeConfidenceEngine:
    """Normalize canonical Zone Quality, HTF Location, and Trend to 0-100."""

    _ALIGNED_LOCATION = {
        "FULL_OVERLAP": 35.0,
        "PARTIAL_OVERLAP": 29.0,
        "TOUCHING": 23.0,
        "NO_OVERLAP": 17.5,
    }
    _OPPOSING_LOCATION = {
        "FULL_OVERLAP": 0.0,
        "PARTIAL_OVERLAP": 6.0,
        "TOUCHING": 12.0,
        "NO_OVERLAP": 17.5,
    }
    _TREND = {
        "ALIGNED": 25.0,
        "NEUTRAL": 12.5,
        "SIDEWAYS": 12.5,
        "UNKNOWN": 12.5,
        "UNAVAILABLE": 12.5,
        "OPPOSING": 0.0,
    }

    @classmethod
    def evaluate(cls, analysis: CanonicalZoneAnalysis) -> CanonicalTradeConfidence:
        quality = cls._quality_value(analysis.zone_quality)
        relationship = (analysis.location_relationship or "NO_OVERLAP").upper()
        compatibility = (analysis.location_compatibility or "NO_HTF_CONTEXT").upper()
        trend = (analysis.trend_alignment or analysis.alignment or "UNKNOWN").upper()
        location_available = compatibility != "NO_HTF_CONTEXT"
        trend_available = trend not in {"UNKNOWN", "UNAVAILABLE"}

        if compatibility == "ALIGNED":
            location_points = cls._ALIGNED_LOCATION.get(relationship, 17.5)
        elif compatibility == "OPPOSING":
            location_points = cls._OPPOSING_LOCATION.get(relationship, 17.5)
        else:
            location_points = 17.5
        trend_points = cls._TREND.get(trend, 12.5)
        total = round(
            min(100.0, max(0.0, quality * 0.40 + location_points + trend_points)), 2
        )

        if location_available and trend_available:
            sufficiency = ContextDataSufficiency.AVAILABLE
        elif location_available or trend_available:
            sufficiency = ContextDataSufficiency.PARTIAL
        else:
            sufficiency = ContextDataSufficiency.INSUFFICIENT

        combined = cls._combined(relationship, compatibility, trend)
        conflicted = trend == "OPPOSING" or (
            compatibility == "OPPOSING" and relationship != "NO_OVERLAP"
        )
        if sufficiency == ContextDataSufficiency.INSUFFICIENT:
            label = TradeConfidenceLabel.INSUFFICIENT_CONTEXT
        elif conflicted:
            label = TradeConfidenceLabel.CONFLICTED
        else:
            label = cls._numeric_label(total)
            if (
                sufficiency == ContextDataSufficiency.PARTIAL
                and label == TradeConfidenceLabel.VERY_HIGH
            ):
                label = TradeConfidenceLabel.HIGH

        reasons = tuple(
            dict.fromkeys(
                (
                    *analysis.reason_codes,
                    f"TRADE_CONFIDENCE_{sufficiency.value}",
                    f"CONTEXT_{combined}",
                )
            )
        )
        evidence = (
            f"Zone Quality {quality:.2f} contributes {quality * .40:.2f}/40.",
            (
                f"HTF Location {compatibility} {relationship} contributes "
                f"{location_points:.2f}/35."
            ),
            f"Canonical Trend alignment {trend} contributes {trend_points:.2f}/25.",
            "This is a deterministic context score, not a probability of profit.",
        )
        return CanonicalTradeConfidence(
            total_score=total,
            label=label,
            zone_quality_score=quality,
            zone_quality_contribution=round(quality * 0.40, 2),
            location_contribution=location_points,
            trend_contribution=trend_points,
            location_alignment=compatibility,
            trend_alignment=trend,
            combined_context=combined,
            htf_overlap_type=relationship,
            htf_direction_compatibility=compatibility,
            data_sufficiency=sufficiency,
            reason_codes=reasons,
            evidence=evidence,
        )

    @staticmethod
    def _quality_value(value: Any) -> float:
        raw = getattr(value, "total_score", value)
        return min(100.0, max(0.0, float(raw)))

    @staticmethod
    def _numeric_label(score: float) -> TradeConfidenceLabel:
        if score >= 85:
            return TradeConfidenceLabel.VERY_HIGH
        if score >= 70:
            return TradeConfidenceLabel.HIGH
        if score >= 50:
            return TradeConfidenceLabel.MODERATE
        return TradeConfidenceLabel.LOW

    @staticmethod
    def _combined(relationship: str, compatibility: str, trend: str) -> str:
        aligned_location = compatibility == "ALIGNED" and relationship != "NO_OVERLAP"
        opposing_location = compatibility == "OPPOSING" and relationship != "NO_OVERLAP"
        if opposing_location or trend == "OPPOSING":
            return "CONFLICTED"
        if aligned_location:
            if trend == "ALIGNED":
                return "ALIGNED"
            if trend in {"NEUTRAL", "SIDEWAYS"}:
                return "LOCATION_SUPPORTED_NEUTRAL_TREND"
            return "LOCATION_SUPPORTED_TREND_UNKNOWN"
        if relationship == "NO_OVERLAP":
            if trend == "ALIGNED":
                return "TREND_SUPPORTED"
            if trend in {"NEUTRAL", "SIDEWAYS"}:
                return "NEUTRAL"
            if trend == "OPPOSING":
                return "CONFLICTED"
            return (
                "PARTIAL_CONTEXT"
                if compatibility != "NO_HTF_CONTEXT"
                else "INSUFFICIENT_CONTEXT"
            )
        if compatibility == "NO_HTF_CONTEXT":
            if trend == "ALIGNED":
                return "TREND_SUPPORTED_LOCATION_UNKNOWN"
            if trend == "OPPOSING":
                return "CONFLICTED"
            if trend in {"NEUTRAL", "SIDEWAYS"}:
                return "PARTIAL_CONTEXT"
            return "INSUFFICIENT_CONTEXT"
        return "PARTIAL_CONTEXT"
