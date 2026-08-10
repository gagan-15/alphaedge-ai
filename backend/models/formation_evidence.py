"""Immutable evidence produced by canonical zone formation."""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.candle_classification import CandleClassification
from backend.models.departure import DepartureDirection, DepartureStrength


@dataclass(frozen=True)
class FormationCandleEvidence:
    """One classified candle and its source timestamp."""

    index: int
    timestamp: str
    classification: CandleClassification


@dataclass(frozen=True)
class CanonicalFormationEvidence:
    """Complete canonical evidence attached to one accepted zone."""

    pattern: str
    leg_in_start_index: int
    leg_in_end_index: int
    leg_in_timestamps: tuple[str, ...]
    leg_in_candles: tuple[FormationCandleEvidence, ...]
    leg_in_direction: DepartureDirection
    base_start_index: int
    base_end_index: int
    base_timestamps: tuple[str, ...]
    base_candles: tuple[FormationCandleEvidence, ...]
    base_body_ratios: tuple[float, ...]
    base_candle_count: int
    leg_out_start_index: int
    leg_out_end_index: int
    leg_out_timestamps: tuple[str, ...]
    leg_out_candles: tuple[FormationCandleEvidence, ...]
    first_leg_out_exciting: bool
    first_leg_out_explosive: bool
    second_leg_out_exciting: bool | None
    second_leg_out_explosive: bool | None
    significant_gap: bool
    gap_measurement: float | None
    departure_strength: DepartureStrength
    closing_rule_passed: bool
    closing_comparison_reference: float
    qualifying_close: float
    acceptance_reason: str
