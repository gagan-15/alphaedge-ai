"""Composition service for the immutable canonical zone analysis read model."""

from __future__ import annotations

from backend.models.canonical_zone_analysis import CanonicalZoneAnalysis
from backend.models.zone import Zone, ZoneType


class CanonicalZoneAnalysisService:
    """Compose existing canonical outputs without rerunning their rules."""

    @staticmethod
    def compose(
        *,
        zone: Zone,
        zone_id: str,
        symbol: str,
        timeframe: str,
        lifecycle: object,
        authenticity: object,
        zone_quality: object,
        canonical_trend: object,
        htf_context: object,
        alignment: str,
        trend_timeframe: str | None = None,
        location_timeframe: str | None = None,
        location_relationship: str = "NO_OVERLAP",
        location_compatibility: str = "NO_HTF_CONTEXT",
        combined_context: object = None,
        data_sufficient: bool = False,
        reason_codes: tuple[str, ...] = (),
    ) -> CanonicalZoneAnalysis:
        evidence = zone.formation_evidence
        demand = zone.zone_type == ZoneType.DEMAND
        return CanonicalZoneAnalysis(
            zone_id=zone_id,
            symbol=symbol.strip().upper(),
            timeframe=timeframe,
            zone_type=zone.zone_type.value,
            pattern=zone.pattern_type,
            proximal=zone.upper_price if demand else zone.lower_price,
            distal=zone.lower_price if demand else zone.upper_price,
            formation_evidence=evidence,
            lifecycle=lifecycle,
            authenticity=authenticity,
            zone_quality=zone_quality,
            canonical_trend=canonical_trend,
            htf_context=htf_context,
            alignment=alignment,
            significant_gap=bool(evidence and evidence.significant_gap),
            gap_measurement=evidence.gap_measurement if evidence else None,
            trend_timeframe=trend_timeframe,
            location_timeframe=location_timeframe,
            trend_alignment=alignment,
            location_relationship=location_relationship,
            location_compatibility=location_compatibility,
            combined_context=combined_context,
            data_sufficient=data_sufficient,
            reason_codes=reason_codes,
        )
