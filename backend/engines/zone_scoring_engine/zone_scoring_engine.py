"""AlphaEdge Canonical Zone Quality Engine using GTF-derived evidence."""

from __future__ import annotations

from backend.config.zone_scoring_config import ZoneScoringConfig
from backend.models.departure import DepartureStrength
from backend.models.zone import Zone, ZoneType
from backend.models.zone_scoring.canonical_zone_quality import (
    ZoneQualityComponent,
    ZoneQualityContext,
)
from backend.models.zone_scoring.zone_score import ZoneScore
from backend.models.zone_scoring.zone_scoring_result import ZoneScoringResult
from backend.validators.zone_scoring_validator import ZoneScoringValidator


class ZoneScoringEngine:
    """Calculate AlphaEdge's deterministic 0-100 Zone Quality Score."""

    def __init__(self, config: ZoneScoringConfig | None = None) -> None:
        self._config = config or ZoneScoringConfig()

    def score(
        self,
        zones: list[Zone],
        contexts: dict[int, ZoneQualityContext] | None = None,
    ) -> ZoneScoringResult:
        ZoneScoringValidator.validate(zones, self._config)
        context_by_index = contexts or {}
        scored = [
            self._score_zone(zone, context_by_index.get(zone.created_index))
            for zone in zones
        ]
        return ZoneScoringResult(scored_zones=scored)

    def _score_zone(self, zone: Zone, context: ZoneQualityContext | None) -> ZoneScore:
        evidence = zone.formation_evidence
        if evidence is None:
            return self._compatibility_score(zone, context)

        components = (
            self._base(evidence),
            self._departure(zone, evidence),
            self._dominance(evidence),
            self._clearance(zone, evidence),
            self._lifecycle(zone, context),
            self._authenticity(context),
        )
        total = round(sum(item.score for item in components), 1)
        reasons = tuple(code for item in components for code in item.reason_codes)
        summary = tuple(fact for item in components for fact in item.evidence)
        by_key = {item.key: item.score for item in components}
        return ZoneScore(
            zone=zone,
            freshness_score=by_key["lifecycle_quality"],
            strength_score=by_key["departure_quality"],
            touch_score=(by_key["legout_dominance"] + by_key["structural_clearance"]),
            merge_bonus=(by_key["base_quality"] + by_key["authenticity_quality"]),
            total_score=total,
            raw_score=total,
            quality_cap=100.0,
            label=self._label(total),
            components=components,
            reason_codes=reasons,
            evidence_summary=summary,
            base_quality_score=by_key["base_quality"],
            departure_quality_score=by_key["departure_quality"],
            legout_dominance_score=by_key["legout_dominance"],
            structural_clearance_score=by_key["structural_clearance"],
            lifecycle_quality_score=by_key["lifecycle_quality"],
            authenticity_quality_score=by_key["authenticity_quality"],
        )

    def _base(self, evidence) -> ZoneQualityComponent:
        ratios = evidence.base_body_ratios
        mean_body = sum(ratios) / len(ratios) if ratios else 1.0
        body_quality = 1.0 - self._clamp(mean_body / 0.5)
        range_values = [
            item.classification.range_to_median
            for item in evidence.base_candles
            if item.classification.range_to_median is not None
        ]
        range_quality = (
            1.0 - self._clamp((sum(range_values) / len(range_values)) / 1.5)
            if range_values
            else 0.5
        )
        normalized = 0.75 * body_quality + 0.25 * range_quality
        score = round(self._config.base_quality_weight * normalized, 2)
        return ZoneQualityComponent(
            "base_quality",
            score,
            self._config.base_quality_weight,
            (
                f"base_count={evidence.base_candle_count}",
                f"mean_body_ratio={mean_body:.4f}",
            ),
            ("LOW_BASE_BODY_RATIO" if mean_body <= 0.25 else "HIGHER_BASE_BODY_RATIO",),
        )

    def _departure(self, zone: Zone, evidence) -> ZoneQualityComponent:
        candles = evidence.leg_out_candles
        count = max(1, len(candles))
        explosive = sum(item.classification.explosive for item in candles) / count
        exciting = (
            sum(item.classification.structure.value == "EXCITING" for item in candles)
            / count
        )
        body_ratio = sum(item.classification.body_ratio for item in candles) / count
        ranges = [
            item.classification.range_to_median
            for item in candles
            if item.classification.range_to_median is not None
        ]
        range_strength = (
            self._clamp((sum(ranges) / len(ranges)) / 2.0) if ranges else 0.5
        )
        width = max(abs(zone.upper_price - zone.lower_price), 1e-9)
        proximal = (
            zone.upper_price if zone.zone_type == ZoneType.DEMAND else zone.lower_price
        )
        displacement = (
            evidence.qualifying_close - proximal
            if zone.zone_type == ZoneType.DEMAND
            else proximal - evidence.qualifying_close
        )
        displacement_ratio = max(0.0, displacement) / width
        displacement_quality = self._clamp(displacement_ratio / 3.0)
        strength_quality = {
            DepartureStrength.WEAK: 0.15,
            DepartureStrength.STRONG: 0.70,
            DepartureStrength.VERY_STRONG: 1.0,
        }[evidence.departure_strength]
        normalized = (
            explosive
            + exciting
            + self._clamp(body_ratio / 0.85)
            + range_strength
            + displacement_quality
            + strength_quality
        ) / 6.0
        score = round(self._config.departure_quality_weight * normalized, 2)
        reasons = [f"{evidence.departure_strength.value}_DEPARTURE"]
        if explosive:
            reasons.append("EXPLOSIVE_LEG_OUT")
        if evidence.significant_gap:
            reasons.append("SIGNIFICANT_GAP")
        if displacement_ratio >= 2:
            reasons.append("HIGH_DISPLACEMENT")
        return ZoneQualityComponent(
            "departure_quality",
            score,
            self._config.departure_quality_weight,
            (
                f"explosive_ratio={explosive:.4f}",
                f"exciting_ratio={exciting:.4f}",
                f"body_ratio={body_ratio:.4f}",
                f"departure_zone_width_ratio={displacement_ratio:.4f}",
            ),
            tuple(reasons),
        )

    def _dominance(self, evidence) -> ZoneQualityComponent:
        leg_in_body = sum(item.classification.body for item in evidence.leg_in_candles)
        leg_out_body = sum(
            item.classification.body for item in evidence.leg_out_candles
        )
        ratio = leg_out_body / max(leg_in_body, 1e-9)
        normalized = self._clamp((ratio - 0.5) / 2.5)
        score = round(self._config.legout_dominance_weight * normalized, 2)
        return ZoneQualityComponent(
            "legout_dominance",
            score,
            self._config.legout_dominance_weight,
            (f"legout_legin_body_ratio={ratio:.4f}",),
            ("LEG_OUT_DOMINATES" if ratio >= 1.5 else "LIMITED_LEG_OUT_DOMINANCE",),
        )

    def _clearance(self, zone: Zone, evidence) -> ZoneQualityComponent:
        width = max(abs(zone.upper_price - zone.lower_price), 1e-9)
        if zone.zone_type == ZoneType.DEMAND:
            clearance = (
                evidence.qualifying_close - evidence.closing_comparison_reference
            )
        else:
            clearance = (
                evidence.closing_comparison_reference - evidence.qualifying_close
            )
        ratio = max(0.0, clearance) / width
        score = round(
            self._config.structural_clearance_weight * self._clamp(ratio / 2.0), 2
        )
        return ZoneQualityComponent(
            "structural_clearance",
            score,
            self._config.structural_clearance_weight,
            (
                f"clearance_zone_width_ratio={ratio:.4f}",
                f"closing_rule_passed={evidence.closing_rule_passed}",
            ),
            (
                (
                    "DECISIVE_STRUCTURAL_CLEARANCE"
                    if ratio >= 1
                    else "MARGINAL_STRUCTURAL_CLEARANCE"
                ),
            ),
        )

    def _lifecycle(
        self, zone: Zone, context: ZoneQualityContext | None
    ) -> ZoneQualityComponent:
        status = (
            (context.lifecycle_status if context else None)
            or ("FRESH" if zone.is_fresh else "TESTED")
        ).upper()
        penetration = max(
            0.0,
            min(100.0, (context.max_penetration_percent if context else None) or 0.0),
        )
        if status in {"FRESH", "APPROACHING", "ACTIVATED"}:
            normalized = 1.0
        elif status in {"REACTING", "TESTING_NOW"}:
            normalized = 0.9 - 0.35 * penetration / 100.0
        elif status in {"TESTED", "TESTED_RESPECTED"}:
            normalized = 0.5
        elif status in {"RETESTED", "MITIGATED"}:
            normalized = 0.25
        else:
            normalized = 0.0
        score = round(self._config.lifecycle_quality_weight * normalized, 2)
        return ZoneQualityComponent(
            "lifecycle_quality",
            score,
            self._config.lifecycle_quality_weight,
            (
                f"lifecycle_status={status}",
                f"max_penetration_percent={penetration:.2f}",
            ),
            (f"LIFECYCLE_{status}",),
        )

    def _authenticity(self, context: ZoneQualityContext | None) -> ZoneQualityComponent:
        status = context.authenticity_status if context else None
        normalized = (
            1.0 if status == "AUTHENTIC" else 0.3 if status == "NON_AUTHENTIC" else 0.5
        )
        reason = (
            "AUTHENTIC_FORMATION"
            if status == "AUTHENTIC"
            else (
                "NON_AUTHENTIC_FORMATION"
                if status == "NON_AUTHENTIC"
                else "AUTHENTICITY_UNAVAILABLE"
            )
        )
        return ZoneQualityComponent(
            "authenticity_quality",
            round(self._config.authenticity_quality_weight * normalized, 2),
            self._config.authenticity_quality_weight,
            (f"authenticity_status={status or 'UNAVAILABLE'}",),
            (reason,),
        )

    def _compatibility_score(
        self, zone: Zone, context: ZoneQualityContext | None
    ) -> ZoneScore:
        # Legacy zones without canonical formation evidence retain their public
        # score behavior. Canonical scanner zones never use this branch.
        freshness = 30.0 if zone.is_fresh else 0.0
        departure = min(max(zone.strength, 0.0), 35.0)
        touch = max(0.0, 20.0 - zone.touch_count * 8.0)
        merge = min(max(0, zone.merged_count - 1) * 7.5, 15.0)
        raw = round(min(freshness + departure + touch + merge, 100.0), 1)
        departure_ratio = departure / 35.0
        if departure_ratio < 0.40:
            cap = 39.0
        elif departure_ratio < 0.60:
            cap = 49.0
        elif departure_ratio < 0.75:
            cap = 69.0
        elif departure_ratio < 0.90:
            cap = 84.0
        else:
            cap = 100.0
        total = min(raw, cap)
        return ZoneScore(
            zone,
            freshness,
            departure,
            touch,
            merge,
            total,
            raw_score=raw,
            quality_cap=cap,
            label=self._label(total),
            reason_codes=("FORMATION_EVIDENCE_UNAVAILABLE",),
            lifecycle_quality_score=freshness,
            departure_quality_score=departure,
            authenticity_quality_score=0.0,
        )

    @staticmethod
    def _label(score: float) -> str:
        if score >= 90:
            return "EXCELLENT"
        if score >= 80:
            return "STRONG"
        if score >= 70:
            return "GOOD"
        if score >= 60:
            return "AVERAGE"
        return "WEAK"

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
