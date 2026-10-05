"""Strict, source-aware rehydration of structured Dhan canonical-zone JSON."""

from __future__ import annotations

from backend.models.candle_classification import CandleClassification, CandleDirection, CandleStructure
from backend.models.departure import DepartureDirection, DepartureStrength
from backend.models.formation_evidence import CanonicalFormationEvidence, FormationCandleEvidence
from backend.models.leg_in_structural_evidence import CanonicalLegInStructuralEvidence, LegInFormationValidity, LegInStructuralState
from backend.models.zone import Zone, ZoneType
from backend.models.zone_boundary import BoundaryMode, BoundaryReasonCode, BoundarySet, ExceptionalBoundarySource, ZoneBoundaryResult


class DhanZoneRehydrationError(ValueError):
    pass


def _classification(value: dict) -> CandleClassification:
    return CandleClassification(index=int(value["index"]), direction=CandleDirection(value["direction"]), structure=CandleStructure(value["structure"]), body=float(value["body"]), candle_range=float(value["candle_range"]), body_ratio=float(value["body_ratio"]), explosive=bool(value["explosive"]), range_to_median=value.get("range_to_median"), close_location=value.get("close_location"))


def _candle(value: dict) -> FormationCandleEvidence:
    return FormationCandleEvidence(index=int(value["index"]), timestamp=str(value["timestamp"]), classification=_classification(value["classification"]))


def _leg_in(value: dict | None) -> CanonicalLegInStructuralEvidence | None:
    if value is None:
        return None
    return CanonicalLegInStructuralEvidence(
        broader_approach_start_index=int(value["broader_approach_start_index"]), broader_approach_end_index=int(value["broader_approach_end_index"]), approach_candle_count=int(value["approach_candle_count"]), leg_in_candle_count=int(value["leg_in_candle_count"]), leg_in_direction=DepartureDirection(value["leg_in_direction"]), directional_displacement=float(value["directional_displacement"]), total_approach_travel=float(value["total_approach_travel"]), directional_efficiency=float(value["directional_efficiency"]), displacement_zone_width_ratio=float(value["displacement_zone_width_ratio"]), displacement_volatility_ratio=value.get("displacement_volatility_ratio"), approach_overlap_ratio=float(value["approach_overlap_ratio"]), prior_zone_occupancy_ratio=float(value["prior_zone_occupancy_ratio"]), pre_leg_in_occupancy_ratio=value.get("pre_leg_in_occupancy_ratio"), adjacent_body_overlap_ratio=float(value["adjacent_body_overlap_ratio"]), approach_direction_changes=int(value["approach_direction_changes"]), pause_candle_count=int(value["pause_candle_count"]), backward_walk_stop_reason=str(value["backward_walk_stop_reason"]), structural_state=LegInStructuralState(value["structural_state"]), reason_codes=tuple(value.get("reason_codes", ())), formation_validity=LegInFormationValidity(value["formation_validity"]), formation_rejection_reasons=tuple(value.get("formation_rejection_reasons", ())),
    )


def _formation(value: dict | None) -> CanonicalFormationEvidence | None:
    if value is None:
        return None
    return CanonicalFormationEvidence(
        pattern=str(value["pattern"]), leg_in_start_index=int(value["leg_in_start_index"]), leg_in_end_index=int(value["leg_in_end_index"]), leg_in_timestamps=tuple(value["leg_in_timestamps"]), leg_in_candles=tuple(_candle(v) for v in value["leg_in_candles"]), leg_in_direction=DepartureDirection(value["leg_in_direction"]), base_start_index=int(value["base_start_index"]), base_end_index=int(value["base_end_index"]), base_timestamps=tuple(value["base_timestamps"]), base_candles=tuple(_candle(v) for v in value["base_candles"]), base_body_ratios=tuple(float(v) for v in value["base_body_ratios"]), base_candle_count=int(value["base_candle_count"]), leg_out_start_index=int(value["leg_out_start_index"]), leg_out_end_index=int(value["leg_out_end_index"]), leg_out_timestamps=tuple(value["leg_out_timestamps"]), leg_out_candles=tuple(_candle(v) for v in value["leg_out_candles"]), first_leg_out_exciting=bool(value["first_leg_out_exciting"]), first_leg_out_explosive=bool(value["first_leg_out_explosive"]), second_leg_out_exciting=value.get("second_leg_out_exciting"), second_leg_out_explosive=value.get("second_leg_out_explosive"), significant_gap=bool(value["significant_gap"]), gap_measurement=value.get("gap_measurement"), departure_strength=DepartureStrength(value["departure_strength"]), closing_rule_passed=bool(value["closing_rule_passed"]), closing_comparison_reference=float(value["closing_comparison_reference"]), qualifying_close=float(value["qualifying_close"]), acceptance_reason=str(value["acceptance_reason"]), leg_in_structural_evidence=_leg_in(value.get("leg_in_structural_evidence")),
    )


def _boundary_set(value: dict | None) -> BoundarySet | None:
    if value is None:
        return None
    source = value.get("exceptional_source")
    return BoundarySet(float(value["proximal"]), float(value["distal"]), BoundaryMode(value["mode"]), ExceptionalBoundarySource(source) if source else None)


def _boundaries(value: dict | None) -> ZoneBoundaryResult | None:
    if value is None:
        return None
    return ZoneBoundaryResult(standard=_boundary_set(value["standard"]), wick_to_wick=_boundary_set(value["wick_to_wick"]), selected=_boundary_set(value["selected"]), exceptional=_boundary_set(value.get("exceptional")), reason_codes=tuple(BoundaryReasonCode(item) for item in value.get("reason_codes", ())))


def rehydrate_zone(payload: dict) -> Zone:
    """Fail closed: incomplete structured evidence is never inferred."""
    try:
        return Zone(zone_type=ZoneType(payload["zone_type"]), upper_price=float(payload["upper_price"]), lower_price=float(payload["lower_price"]), created_index=int(payload["created_index"]), strength=float(payload.get("strength", 0.0)), is_fresh=bool(payload.get("is_fresh", True)), touch_count=int(payload.get("touch_count", 0)), merged_count=int(payload.get("merged_count", 1)), pattern_type=payload.get("pattern_type"), boundary_result=_boundaries(payload.get("boundary_result")), formation_evidence=_formation(payload.get("formation_evidence")))
    except (KeyError, TypeError, ValueError) as error:
        raise DhanZoneRehydrationError(str(error)) from error
