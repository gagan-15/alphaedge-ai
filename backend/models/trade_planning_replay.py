"""Immutable records for the Milestone 8 historical planning replay."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReplayEntryPolicy(str, Enum):
    """Candidate interaction prices studied without production activation."""

    PROXIMAL = "PROXIMAL"
    MIDPOINT = "MIDPOINT"
    DISTAL = "DISTAL"


class ReplayOutcome(str, Enum):
    """Observable forward outcomes; ambiguous bars are never guessed."""

    TARGET_BEFORE_STOP = "TARGET_BEFORE_STOP"
    STOP_BEFORE_TARGET = "STOP_BEFORE_TARGET"
    AMBIGUOUS_SAME_CANDLE = "AMBIGUOUS_SAME_CANDLE"
    OPEN_AT_END = "OPEN_AT_END"
    ENTRY_NOT_REACHED = "ENTRY_NOT_REACHED"
    NO_VALID_OPPOSING_ZONE = "NO_VALID_OPPOSING_ZONE"


@dataclass(frozen=True)
class ReplayStopPolicy:
    """One auditable protective-buffer candidate."""

    name: str
    zone_width_fraction: float = 0.0
    atr_fraction: float = 0.0
    hybrid: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Stop policy name is required.")
        if self.zone_width_fraction < 0 or self.atr_fraction < 0:
            raise ValueError("Stop components cannot be negative.")
        if self.zone_width_fraction == 0 and self.atr_fraction == 0:
            raise ValueError("At least one stop component is required.")


@dataclass(frozen=True)
class ReplayPlanSnapshot:
    """Plan facts frozen using only information known at planning time."""

    zone_id: str
    symbol: str
    timeframe: str
    pattern: str
    zone_type: str
    planning_index: int
    planning_timestamp: str
    interaction_low: float
    interaction_high: float
    structural_invalidation: float
    opposing_zone_id: str | None
    structural_target: float | None
    atr14: float | None
    prefix_candle_count: int
    known_zone_count: int
    target_eligible_zone_count: int
    target_availability_reason: str
    selected_lifecycle_status: str
    selected_authenticity_status: str
    tick_size: float | None = None


@dataclass(frozen=True)
class ReplayObservation:
    """Outcome of one entry and stop combination for one frozen snapshot."""

    zone_id: str
    symbol: str
    timeframe: str
    pattern: str
    zone_type: str
    entry_policy: ReplayEntryPolicy
    stop_policy: str
    entry_price: float
    stop_price: float
    target_price: float | None
    risk_per_share: float
    reward_per_share: float | None
    structural_risk_reward: float | None
    entry_index: int | None
    entry_timestamp: str | None
    candles_to_entry: int | None
    outcome: ReplayOutcome
    outcome_index: int | None
    outcome_timestamp: str | None
    first_stop_index: int | None
    first_stop_timestamp: str | None
    first_target_index: int | None
    first_target_timestamp: str | None
    first_structural_failure_index: int | None
    first_structural_failure_timestamp: str | None
    future_candle_count: int
    mae_price: float | None
    mfe_price: float | None
    mae_zone_width: float | None
    mfe_zone_width: float | None
    mae_atr: float | None
    mfe_atr: float | None
    mae_before_target_price: float | None
    mae_before_target_zone_width: float | None
    mae_before_target_atr: float | None
    distal_breached_before_target: bool
