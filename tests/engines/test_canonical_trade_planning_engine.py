from dataclasses import replace

import pytest

from backend.config.canonical_methodology import (
    CANONICAL_TRADE_PLANNING_VERSION,
)
from backend.engines.trade_planning_engine import CanonicalTradePlanningEngine
from backend.models.canonical_trade_plan import (
    CanonicalPlanningZone,
    CanonicalTradePlanStatus,
    TradePlanReasonCode,
)


VERSION = "formation-1.1"
SNAPSHOT = "TCS:1D:2026-08-17"


def test_canonical_trade_planning_version_is_frozen_at_v1() -> None:
    assert CANONICAL_TRADE_PLANNING_VERSION == "1"


def zone(
    zone_id: str,
    zone_type: str,
    proximal: float,
    distal: float,
    **changes: object,
) -> CanonicalPlanningZone:
    base = CanonicalPlanningZone(
        zone_id=zone_id,
        symbol="TCS",
        timeframe="1D",
        snapshot_id=SNAPSHOT,
        methodology_version=VERSION,
        zone_type=zone_type,
        proximal=proximal,
        distal=distal,
        formation_evidence_available=True,
        authenticity_status="AUTHENTIC",
        lifecycle_status="FRESH",
        is_active=True,
        is_removed=False,
    )
    return replace(base, **changes)


def build(
    selected: CanonicalPlanningZone,
    *others: CanonicalPlanningZone,
):
    return CanonicalTradePlanningEngine().build(
        selected,
        (selected, *others),
        expected_snapshot_id=SNAPSHOT,
        expected_methodology_version=VERSION,
    )


def test_demand_uses_proximal_entry_and_distal_invalidation() -> None:
    result = build(zone("D1", "DEMAND", 105, 100))
    assert result.planned_entry_reference == 105
    assert result.structural_invalidation == 100


def test_supply_uses_proximal_entry_and_distal_invalidation() -> None:
    result = build(zone("S1", "SUPPLY", 125, 130))
    assert result.planned_entry_reference == 125
    assert result.structural_invalidation == 130


def test_demand_uses_nearest_eligible_supply_proximal() -> None:
    result = build(
        zone("D1", "DEMAND", 105, 100),
        zone("S2", "SUPPLY", 145, 150),
        zone("S1", "SUPPLY", 120, 125),
    )
    assert result.target == 120
    assert result.target_zone_id == "S1"
    assert result.available_room == 15


def test_supply_uses_nearest_eligible_demand_proximal() -> None:
    result = build(
        zone("S1", "SUPPLY", 125, 130),
        zone("D2", "DEMAND", 90, 85),
        zone("D1", "DEMAND", 110, 105),
    )
    assert result.target == 110
    assert result.target_zone_id == "D1"
    assert result.available_room == 15


@pytest.mark.parametrize(
    ("change", "value"),
    [
        ("lifecycle_status", "INVALIDATED"),
        ("lifecycle_status", "REMOVED"),
        ("authenticity_status", "NON_AUTHENTIC"),
        ("timeframe", "1W"),
        ("snapshot_id", "OTHER"),
    ],
)
def test_ineligible_opposing_zone_is_excluded(change: str, value: str) -> None:
    candidate = zone("S1", "SUPPLY", 120, 125)
    candidate = replace(
        candidate,
        **{change: value},
        is_active=value not in {"INVALIDATED", "REMOVED"},
        is_removed=value == "REMOVED",
    )
    result = build(zone("D1", "DEMAND", 105, 100), candidate)
    assert result.status == CanonicalTradePlanStatus.PARTIAL
    assert result.target is None


def test_close_opposing_target_is_not_skipped_for_better_room() -> None:
    result = build(
        zone("D1", "DEMAND", 105, 100),
        zone("CLOSE", "SUPPLY", 106, 108),
        zone("FAR", "SUPPLY", 150, 155),
    )
    assert result.target_zone_id == "CLOSE"
    assert result.structural_reward_per_share == 1


def test_no_target_returns_partial_without_manufactured_values() -> None:
    result = build(zone("D1", "DEMAND", 105, 100))
    assert result.status == CanonicalTradePlanStatus.PARTIAL
    assert result.target is None
    assert result.available_room is None
    assert result.structural_reward_per_share is None
    assert TradePlanReasonCode.NO_VALID_OPPOSING_ZONE in result.reason_codes


def test_protective_stop_and_risk_reward_are_never_invented() -> None:
    result = build(
        zone("D1", "DEMAND", 105, 100),
        zone("S1", "SUPPLY", 120, 125),
    )
    assert result.protective_stop is None
    assert result.risk_per_share is None
    assert result.risk_reward is None
    assert result.distance_entry_to_structural_invalidation == 5
    assert TradePlanReasonCode.PROTECTIVE_STOP_REQUIRES_EXECUTION_POLICY in (
        result.reason_codes
    )


def test_direction_is_not_masked_with_absolute_value() -> None:
    result = build(
        zone("D1", "DEMAND", 105, 100),
        zone("BEHIND", "SUPPLY", 95, 98),
    )
    assert result.status == CanonicalTradePlanStatus.PARTIAL
    assert result.target is None


def test_selected_immutable_identity_is_preserved() -> None:
    selected = zone("IMMUTABLE-ID", "DEMAND", 105, 100)
    result = build(selected, zone("S1", "SUPPLY", 120, 125))
    assert result.selected_zone_id == selected.zone_id
    assert result.snapshot_id == selected.snapshot_id


def test_out_of_sync_selected_zone_is_unavailable() -> None:
    selected = zone("D1", "DEMAND", 105, 100)
    stale = replace(selected, proximal=106)
    result = CanonicalTradePlanningEngine().build(
        stale,
        (selected,),
        expected_snapshot_id=SNAPSHOT,
        expected_methodology_version=VERSION,
    )
    assert result.status == CanonicalTradePlanStatus.UNAVAILABLE
    assert TradePlanReasonCode.SELECTED_ZONE_OUT_OF_SYNC in result.reason_codes


def test_stale_methodology_cannot_produce_plan() -> None:
    selected = zone(
        "D1", "DEMAND", 105, 100, methodology_version="formation-1.0"
    )
    result = CanonicalTradePlanningEngine().build(
        selected,
        (selected,),
        expected_snapshot_id=SNAPSHOT,
        expected_methodology_version=VERSION,
    )
    assert result.status == CanonicalTradePlanStatus.UNAVAILABLE
    assert TradePlanReasonCode.STALE_METHODOLOGY_VERSION in result.reason_codes


@pytest.mark.parametrize(
    "selected",
    [
        zone(
            "D1", "DEMAND", 105, 100,
            lifecycle_status="INVALIDATED", is_active=False,
        ),
        zone(
            "D1", "DEMAND", 105, 100,
            lifecycle_status="REMOVED", is_active=False, is_removed=True,
        ),
        zone("D1", "DEMAND", 100, 105),
        zone("D1", "DEMAND", 105, 105),
        zone("D1", "DEMAND", 105, 100, formation_evidence_available=False),
    ],
)
def test_unsafe_selected_zone_is_unavailable(selected: CanonicalPlanningZone) -> None:
    result = build(selected)
    assert result.status == CanonicalTradePlanStatus.UNAVAILABLE


def test_complete_structural_plan_has_positive_directional_reward() -> None:
    result = build(
        zone("D1", "DEMAND", 105, 100),
        zone("S1", "SUPPLY", 120, 125),
    )
    assert result.status == CanonicalTradePlanStatus.COMPLETE_STRUCTURAL
    assert result.structural_reward_per_share == 15
    assert TradePlanReasonCode.PLAN_STRUCTURAL_COMPLETE in result.reason_codes
