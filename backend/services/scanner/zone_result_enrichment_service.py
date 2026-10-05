"""One source-aware downstream enrichment path for canonical zones.

This module deliberately accepts already-created :class:`Zone` objects.  It
does not import the detector and therefore cannot re-run formation for a
persisted-provider result.
"""

from __future__ import annotations

from dataclasses import dataclass

from pandas import DataFrame

from backend.api.models.scanner_response import (
    ZoneExplanationFactorResponse,
    ZoneExplanationResponse,
    ZoneQualityComponentResponse,
    ZoneResearchResultResponse,
)
from backend.engines.zone_scoring_engine.zone_scoring_engine import ZoneScoringEngine
from backend.models.zone import Zone, ZoneType
from backend.models.zone_scoring.canonical_zone_quality import ZoneQualityContext
from backend.services.scanner.dashboard_zone_qualification_service import (
    DashboardZoneQualificationService,
)
from backend.services.scanner.zone_lifecycle_ui_service import ZoneLifecycleUiService
from backend.services.zone_explanation_service import ZoneExplanationService


@dataclass(frozen=True)
class EnrichedZoneBatch:
    """The exact scanner-ready records produced for one symbol/frame."""

    active: tuple[ZoneResearchResultResponse, ...]
    historical: tuple[ZoneResearchResultResponse, ...]
    base_preferences: dict[int, int]
    canonical_zone_count: int
    formation_qualified_count: int
    dashboard_qualified_count: int
    qualification_rejection_counts: dict[str, int]
    lifecycle_counts: dict[str, int]


class ZoneResultEnrichmentService:
    """Enrich detected or strictly rehydrated zones with frozen engines only."""

    _tracked_rejections = {
        "WEAK_DEPARTURE", "BASE_TOO_LONG_FOR_PRIMARY_DASHBOARD",
        "MULTI_BASE_EXECUTION_ZONE", "INSUFFICIENT_DISPLACEMENT",
        "POOR_DIRECTIONAL_CLOSE", "MALFORMED_OR_INCOMPLETE_EVIDENCE",
        "DRIFTING_DEPARTURE", "NO_EXPLOSIVE_OR_STRONG_SEQUENCE",
        "CLOSING_RULE_FAILED",
    }

    def __init__(self) -> None:
        self._qualification = DashboardZoneQualificationService()
        self._lifecycle = ZoneLifecycleUiService()
        self._scoring = ZoneScoringEngine()

    @staticmethod
    def _gap_type(zone: Zone) -> str | None:
        evidence = zone.formation_evidence
        if evidence is None or not evidence.significant_gap:
            return None
        return "GAP UP" if evidence.leg_in_direction.value == "BULLISH" else "GAP DOWN"

    @staticmethod
    def _formation_anchor(zone: Zone, data: DataFrame) -> tuple[int, str]:
        """Return the immutable canonical Base anchor for result/chart consumers.

        ``created_index`` is zone identity metadata; it is not guaranteed to
        be the first Base candle.  Charting must instead use the formation
        evidence produced by the frozen formation engine.
        """
        evidence = zone.formation_evidence
        if evidence and evidence.base_timestamps:
            return evidence.base_start_index, str(evidence.base_timestamps[0])[:10]
        return zone.created_index, data.index[zone.created_index].date().isoformat()

    def enrich(
        self, *, zones: list[Zone], data: DataFrame, symbol: str,
        timeframe: str, current_price: float | None = None,
    ) -> EnrichedZoneBatch:
        """Return scanner rows without detecting, altering, or reconstructing zones."""
        if data.empty:
            raise ValueError("Cannot enrich a zone without persisted candle data.")
        price = float(data["Close"].iloc[-1]) if current_price is None else float(current_price)
        qualifications = {
            zone.created_index: self._qualification.qualify(zone, timeframe)
            for zone in zones
        }
        metadata = self._lifecycle.evaluate(
            zones, data, symbol=symbol, timeframe=timeframe, current_price=price,
        )
        rejected: dict[str, int] = {}
        counts = {
            "total": 0, "fresh": 0, "reacting": 0, "tested": 0,
            "retested": 0, "invalidated": 0, "authentic": 0,
            "non_authentic": 0,
        }
        qualified = 0
        for zone in zones:
            facts = metadata.get(zone.created_index)
            if facts is None:
                continue
            counts["total"] += 1
            if facts.test_count == 0 and facts.lifecycle_status not in ("INVALIDATED", "REMOVED"):
                counts["fresh"] += 1
            if facts.lifecycle_status == "REACTING": counts["reacting"] += 1
            if facts.test_count == 1: counts["tested"] += 1
            if facts.test_count >= 2: counts["retested"] += 1
            if facts.lifecycle_status in ("INVALIDATED", "REMOVED"): counts["invalidated"] += 1
            counts["authentic" if facts.authenticity_status == "AUTHENTIC" else "non_authentic"] += 1
            qualification = qualifications[zone.created_index]
            if not qualification.dashboard_qualified:
                for reason in qualification.qualification_reason_codes:
                    if reason in self._tracked_rejections:
                        rejected[reason] = rejected.get(reason, 0) + 1
            elif facts.dashboard_lifecycle_eligible:
                qualified += 1
            else:
                reason = facts.dashboard_lifecycle_reason_code
                rejected[reason] = rejected.get(reason, 0) + 1

        formation = [zone for zone in sorted(zones, key=lambda item: item.created_index, reverse=True)
                     if qualifications[zone.created_index].dashboard_qualified]
        active = [zone for zone in formation if metadata[zone.created_index].dashboard_lifecycle_eligible][:4]
        historical = [zone for zone in formation[:4]
                      if metadata[zone.created_index].is_invalidated and zone not in active]
        preferences: dict[int, int] = {}

        def response_for(zone: Zone) -> ZoneResearchResultResponse:
            qualification = qualifications[zone.created_index]
            facts = metadata[zone.created_index]
            invalidated = facts.is_invalidated
            if invalidated:
                status, distance = "INVALIDATED", 0.0
            elif facts.dashboard_lifecycle_reason_code == "LIFECYCLE_REACTING":
                status = "REACTING"
                proximal = zone.upper_price if zone.zone_type == ZoneType.DEMAND else zone.lower_price
                distance = abs(price - proximal) / price * 100
            elif zone.lower_price <= price <= zone.upper_price:
                status, distance = "IN ZONE", 0.0
            elif price > zone.upper_price:
                distance = (price - zone.upper_price) / price * 100
                status = "APPROACHING" if distance <= 5 else "WATCH"
            else:
                distance = (zone.lower_price - price) / price * 100
                status = "APPROACHING" if distance <= 5 else "WATCH"
            score = self._scoring.score([zone], {zone.created_index: ZoneQualityContext(
                lifecycle_status=facts.lifecycle_status, is_fresh=facts.is_fresh,
                penetration_percent=facts.current_penetration_percent,
                max_penetration_percent=facts.max_penetration_percent,
                authenticity_status=facts.authenticity_status,
            )}).scored_zones[0]
            explanation = ZoneExplanationService.build(zone, score)
            gap_type = self._gap_type(zone)
            formation_index, formation_date = self._formation_anchor(zone, data)
            demand = zone.zone_type == ZoneType.DEMAND
            preferences[zone.created_index] = qualification.base_preference_rank
            evidence = (
                "Fresh: price has not retested the zone after formation." if facts.is_fresh else f"Tested: {facts.test_count} distinct post-formation visit(s) reduce quality.",
                f"Departure quality contribution: {score.departure_quality_score:.1f}/30.",
                f"Leg-Out dominance contribution: {score.legout_dominance_score:.1f}/15.",
                f"Structural clearance contribution: {score.structural_clearance_score:.1f}/15.",
                "This quality score is rule-based and is not a probability that the zone will hold.",
                f"Departure includes a confirmed {gap_type.lower()}." if gap_type else "No non-overlapping departure gap was detected.",
            )
            return ZoneResearchResultResponse(
                symbol=symbol, zone_type=zone.zone_type.value, pattern_type=zone.pattern_type,
                gap_type=gap_type, proximal_price=zone.upper_price if demand else zone.lower_price,
                distal_price=zone.lower_price if demand else zone.upper_price,
                distance_percent=round(distance, 2), zone_score=round(score.total_score, 1),
                freshness_score=round(score.freshness_score, 1), strength_score=round(score.strength_score, 1),
                touch_score=round(score.touch_score, 1), merge_score=round(score.merge_bonus, 1),
                raw_zone_score=round(score.raw_score, 1), quality_cap=round(score.quality_cap, 1),
                zone_quality_label=score.label, zone_quality_components={c.key: round(c.score, 2) for c in score.components},
                zone_quality_component_details=tuple(ZoneQualityComponentResponse(key=c.key, score=round(c.score, 2), maximum_score=round(c.maximum_score, 2), evidence=c.evidence, reason_codes=c.reason_codes) for c in score.components),
                zone_quality_reason_codes=score.reason_codes, is_fresh=facts.is_fresh,
                touch_count=facts.test_count, merged_count=zone.merged_count, evidence=evidence,
                explanation=ZoneExplanationResponse(overall_score=explanation.overall_score, rating=explanation.rating, label=explanation.label, summary=explanation.summary,
                    positive_factors=tuple(ZoneExplanationFactorResponse(key=f.key, title=f.title, score=f.score, sentiment=f.sentiment, summary=f.summary, recommendation=f.recommendation, weight=f.weight) for f in explanation.positive_factors),
                    negative_factors=tuple(ZoneExplanationFactorResponse(key=f.key, title=f.title, score=f.score, sentiment=f.sentiment, summary=f.summary, recommendation=f.recommendation, weight=f.weight) for f in explanation.negative_factors), educational_insight=explanation.educational_insight),
                current_price=price, timeframe=timeframe, base_index=formation_index,
                base_date=formation_date, status=status,
                reaction_percent=facts.reaction_percentage, zone_id=facts.zone_id,
                lifecycle_status=facts.lifecycle_status, authenticity_status=facts.authenticity_status,
                authenticity_reason_code=facts.authenticity_reason_code, authenticity_reason=facts.authenticity_reason,
                test_count=facts.test_count, reaction_status=facts.reaction_status,
                reaction_percentage=facts.reaction_percentage, max_penetration_percent=facts.max_penetration_percent,
                current_penetration_percent=facts.current_penetration_percent, good_closing=facts.good_closing,
                parent_zone_id=facts.parent_zone_id, is_nested=facts.is_nested, is_duplicate=facts.is_duplicate,
                overlap_percent=facts.overlap_percent, dashboard_qualified=facts.dashboard_lifecycle_eligible,
                qualification_reason_codes=qualification.qualification_reason_codes + (facts.dashboard_lifecycle_reason_code,),
                departure_quality=qualification.departure_quality,
                canonical_formation_departure=zone.formation_evidence.departure_strength.value if zone.formation_evidence else None,
                dashboard_qualification_departure=qualification.departure_quality, base_quality=qualification.base_quality,
                formation_quality=qualification.formation_quality, departure_displacement=qualification.departure_displacement,
                departure_zone_width_ratio=qualification.departure_zone_width_ratio, base_candle_count=qualification.base_candle_count,
                base_compactness=qualification.base_compactness, base_compactness_reason=qualification.base_compactness_reason,
            )

        return EnrichedZoneBatch(
            active=tuple(response_for(zone) for zone in active),
            historical=tuple(response_for(zone) for zone in historical),
            base_preferences=preferences, canonical_zone_count=len(zones),
            formation_qualified_count=sum(q.dashboard_qualified for q in qualifications.values()),
            dashboard_qualified_count=qualified, qualification_rejection_counts=rejected,
            lifecycle_counts=counts,
        )
