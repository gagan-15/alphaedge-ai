"""Immutable models for AlphaEdge Canonical Trade Planning V1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CanonicalTradePlanStatus(str, Enum):
    """Completeness of a structural, research-only trade plan."""

    COMPLETE_STRUCTURAL = "COMPLETE_STRUCTURAL"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"


class ProtectiveStopStatus(str, Enum):
    """Protective-stop policy state for the structural plan."""

    POLICY_NOT_DEFINED = "POLICY_NOT_DEFINED"


class TradePlanReasonCode(str, Enum):
    """Deterministic explanations returned by the canonical engine."""

    PLAN_STRUCTURAL_COMPLETE = "PLAN_STRUCTURAL_COMPLETE"
    NO_VALID_OPPOSING_ZONE = "NO_VALID_OPPOSING_ZONE"
    PROTECTIVE_STOP_REQUIRES_EXECUTION_POLICY = (
        "PROTECTIVE_STOP_REQUIRES_EXECUTION_POLICY"
    )
    SELECTED_ZONE_NOT_FOUND = "SELECTED_ZONE_NOT_FOUND"
    SELECTED_ZONE_OUT_OF_SYNC = "SELECTED_ZONE_OUT_OF_SYNC"
    STALE_METHODOLOGY_VERSION = "STALE_METHODOLOGY_VERSION"
    ZONE_INVALIDATED = "ZONE_INVALIDATED"
    ZONE_REMOVED = "ZONE_REMOVED"
    SNAPSHOT_MISMATCH = "SNAPSHOT_MISMATCH"
    INVALID_CANONICAL_BOUNDARIES = "INVALID_CANONICAL_BOUNDARIES"
    TARGET_NOT_IN_TRADE_DIRECTION = "TARGET_NOT_IN_TRADE_DIRECTION"
    NON_POSITIVE_STRUCTURAL_REWARD = "NON_POSITIVE_STRUCTURAL_REWARD"
    MARKET_DATA_UNAVAILABLE = "MARKET_DATA_UNAVAILABLE"


@dataclass(frozen=True)
class CanonicalPlanningZone:
    """Exact canonical zone coordinates and eligibility from one snapshot."""

    zone_id: str
    symbol: str
    timeframe: str
    snapshot_id: str
    methodology_version: str
    zone_type: str
    proximal: float
    distal: float
    formation_evidence_available: bool
    authenticity_status: str
    lifecycle_status: str
    is_active: bool
    is_removed: bool


@dataclass(frozen=True)
class CanonicalTradePlan:
    """Canonical structural plan; never an execution or brokerage instruction."""

    selected_zone_id: str
    symbol: str
    timeframe: str
    snapshot_id: str
    methodology_version: str
    zone_type: str
    status: CanonicalTradePlanStatus
    interaction_range: tuple[float, float] | None
    planned_entry_reference: float | None
    structural_invalidation: float | None
    target: float | None
    target_zone_id: str | None
    available_room: float | None
    structural_reward_per_share: float | None
    distance_entry_to_structural_invalidation: float | None
    protective_stop: float | None
    protective_stop_status: ProtectiveStopStatus
    risk_per_share: float | None
    risk_reward: float | None
    reason_codes: tuple[TradePlanReasonCode, ...]
    research_only: bool = True

    def as_dict(self) -> dict[str, object]:
        """Serialize without changing the canonical values."""

        return {
            "selected_zone_id": self.selected_zone_id,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "snapshot_id": self.snapshot_id,
            "methodology_version": self.methodology_version,
            "zone_type": self.zone_type,
            "status": self.status.value,
            "interaction_range": (
                list(self.interaction_range) if self.interaction_range else None
            ),
            "planned_entry_reference": self.planned_entry_reference,
            "structural_invalidation": self.structural_invalidation,
            "target": self.target,
            "target_zone_id": self.target_zone_id,
            "available_room": self.available_room,
            "structural_reward_per_share": self.structural_reward_per_share,
            "distance_entry_to_structural_invalidation": (
                self.distance_entry_to_structural_invalidation
            ),
            "protective_stop": self.protective_stop,
            "protective_stop_status": self.protective_stop_status.value,
            "risk_per_share": self.risk_per_share,
            "risk_reward": self.risk_reward,
            "reason_codes": [reason.value for reason in self.reason_codes],
            "research_only": self.research_only,
        }
