"""Immutable shadow evidence describing the approach into a canonical Base."""

from dataclasses import dataclass
from enum import Enum

from backend.models.departure import DepartureDirection


class LegInStructuralState(str, Enum):
    CLEAN = "CLEAN"
    ACCEPTABLE = "ACCEPTABLE"
    BORDERLINE = "BORDERLINE"
    CONGESTED = "CONGESTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class LegInFormationValidity(str, Enum):
    """Narrow canonical V1 formation decision; shadow state remains diagnostic."""

    VALID = "LEG_IN_STRUCTURE_VALID"
    INVALID_CLEAR_CONGESTION = "LEG_IN_STRUCTURE_INVALID_CLEAR_CONGESTION"


@dataclass(frozen=True)
class CanonicalLegInStructuralEvidence:
    """Shadow-only deterministic measurements; never an eligibility result."""

    broader_approach_start_index: int
    broader_approach_end_index: int
    approach_candle_count: int
    leg_in_candle_count: int
    leg_in_direction: DepartureDirection
    directional_displacement: float
    total_approach_travel: float
    directional_efficiency: float
    displacement_zone_width_ratio: float
    displacement_volatility_ratio: float | None
    approach_overlap_ratio: float
    prior_zone_occupancy_ratio: float
    pre_leg_in_occupancy_ratio: float | None
    adjacent_body_overlap_ratio: float
    approach_direction_changes: int
    pause_candle_count: int
    backward_walk_stop_reason: str
    structural_state: LegInStructuralState
    reason_codes: tuple[str, ...]
    formation_validity: LegInFormationValidity
    formation_rejection_reasons: tuple[str, ...]
