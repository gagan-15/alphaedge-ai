"""Milestone 8 replay isolation, direction, and look-ahead tests."""

from dataclasses import replace

import pandas as pd

from backend.models.candle_classification import (
    CandleClassification,
    CandleDirection,
    CandleStructure,
)
from backend.models.departure import DepartureDirection, DepartureStrength
from backend.models.formation_evidence import (
    CanonicalFormationEvidence,
    FormationCandleEvidence,
)
from backend.models.trade_planning_replay import (
    ReplayEntryPolicy,
    ReplayOutcome,
    ReplayStopPolicy,
)
from backend.models.zone import Zone, ZoneType
from backend.research.trade_planning_replay import (
    ATR_STOP_POLICIES,
    REPLAY_HORIZON_V1,
    ZONE_WIDTH_STOP_POLICIES,
    TradePlanningReplayEngine,
)


def candles() -> pd.DataFrame:
    index = pd.date_range("2025-01-01", periods=40, freq="D")
    close = [100 + item * 0.5 for item in range(40)]
    return pd.DataFrame(
        {
            "Open": [item - 0.2 for item in close],
            "High": [item + 1 for item in close],
            "Low": [item - 1 for item in close],
            "Close": close,
            "Volume": [1000] * 40,
        },
        index=index,
    )


def evidence(pattern: str, end: int) -> CanonicalFormationEvidence:
    classification = CandleClassification(
        index=end - 2,
        structure=CandleStructure.EXCITING,
        direction=CandleDirection.BULLISH,
        body=1.0,
        candle_range=2.0,
        body_ratio=0.5,
        explosive=False,
    )
    item = FormationCandleEvidence(end - 2, str(end - 2), classification)
    return CanonicalFormationEvidence(
        pattern=pattern,
        leg_in_start_index=end - 2,
        leg_in_end_index=end - 2,
        leg_in_timestamps=(str(end - 2),),
        leg_in_candles=(item,),
        leg_in_direction=DepartureDirection.BULLISH,
        base_start_index=end - 1,
        base_end_index=end - 1,
        base_timestamps=(str(end - 1),),
        base_candles=(replace(item, index=end - 1),),
        base_body_ratios=(0.3,),
        base_candle_count=1,
        leg_out_start_index=end,
        leg_out_end_index=end,
        leg_out_timestamps=(str(end),),
        leg_out_candles=(replace(item, index=end),),
        first_leg_out_exciting=True,
        first_leg_out_explosive=True,
        second_leg_out_exciting=None,
        second_leg_out_explosive=None,
        significant_gap=False,
        gap_measurement=None,
        departure_strength=DepartureStrength.STRONG,
        closing_rule_passed=True,
        closing_comparison_reference=100,
        qualifying_close=105,
        acceptance_reason="fixture",
    )


class PrefixDetector:
    """Detector whose output proves replay depends only on prefix length."""

    def detect_zones(self, data: pd.DataFrame) -> list[Zone]:
        zones = []
        if len(data) >= 11:
            zones.append(
                Zone(
                    ZoneType.DEMAND,
                    105,
                    100,
                    8,
                    pattern_type="DBR",
                    formation_evidence=evidence("DBR", 10),
                )
            )
        if len(data) >= 16:
            zones.append(
                Zone(
                    ZoneType.SUPPLY,
                    120,
                    115,
                    13,
                    pattern_type="RBD",
                    formation_evidence=evidence("RBD", 15),
                )
            )
        return zones


def test_snapshot_uses_only_zones_formed_by_planning_time() -> None:
    result = TradePlanningReplayEngine(PrefixDetector()).replay(
        candles(),
        symbol="TEST",
        timeframe="1D",
        entry_policies=(ReplayEntryPolicy.PROXIMAL,),
        stop_policies=(ReplayStopPolicy("ZW10", zone_width_fraction=0.1),),
    )
    demand = next(item for item in result.snapshots if item.zone_type == "DEMAND")
    assert demand.known_zone_count == 1
    assert demand.structural_target is None
    assert demand.opposing_zone_id is None
    assert demand.target_availability_reason == "OPPOSING_FORMED_LATER"


def test_future_mutation_cannot_change_frozen_plan_snapshot() -> None:
    original = candles()
    changed = original.copy()
    changed.iloc[20:, changed.columns.get_loc("High")] += 500
    changed.iloc[20:, changed.columns.get_loc("Close")] += 400
    first = TradePlanningReplayEngine(PrefixDetector()).replay(
        original, symbol="TEST", timeframe="1D"
    )
    second = TradePlanningReplayEngine(PrefixDetector()).replay(
        changed, symbol="TEST", timeframe="1D"
    )
    assert first.snapshots == second.snapshots


def test_directional_math_never_uses_absolute_value() -> None:
    result = TradePlanningReplayEngine(PrefixDetector()).replay(
        candles(),
        symbol="TEST",
        timeframe="1D",
        entry_policies=(ReplayEntryPolicy.PROXIMAL,),
        stop_policies=(ReplayStopPolicy("ZW10", zone_width_fraction=0.1),),
    )
    demand = next(item for item in result.observations if item.zone_type == "DEMAND")
    assert demand.entry_price == 105
    assert demand.stop_price == 99.5
    assert demand.risk_per_share == 5.5
    assert demand.outcome in set(ReplayOutcome)


def test_wilder_atr_uses_only_prior_and_current_true_ranges() -> None:
    data = candles()
    prefix = data.iloc[:20]
    original = TradePlanningReplayEngine(PrefixDetector()).replay(
        data, symbol="TEST", timeframe="1D"
    )
    mutated = data.copy()
    mutated.iloc[20:, mutated.columns.get_loc("Low")] -= 1000
    changed = TradePlanningReplayEngine(PrefixDetector()).replay(
        mutated, symbol="TEST", timeframe="1D"
    )
    assert original.snapshots == changed.snapshots
    assert len(prefix) == 20


def test_missing_tick_size_is_explicit_and_not_assumed() -> None:
    result = TradePlanningReplayEngine(PrefixDetector()).replay(
        candles(), symbol="TEST", timeframe="1D"
    )
    assert result.snapshots
    assert all(item.tick_size is None for item in result.snapshots)
    assert any("tick-size metadata unavailable" in item for item in result.limitations)


def test_replay_preserves_first_stop_and_later_target_for_calibration() -> None:
    class TargetKnownDetector:
        def detect_zones(self, data: pd.DataFrame) -> list[Zone]:
            if len(data) < 11:
                return []
            return [
                Zone(
                    ZoneType.SUPPLY,
                    120,
                    115,
                    6,
                    pattern_type="RBD",
                    formation_evidence=evidence("RBD", 8),
                ),
                Zone(
                    ZoneType.DEMAND,
                    105,
                    100,
                    8,
                    pattern_type="DBR",
                    formation_evidence=evidence("DBR", 10),
                ),
            ]

    data = candles()
    # Demand enters at 105, crosses a 99.5 stop, then later reaches the
    # prefix-valid 115 supply target. The primary outcome remains stop-first,
    # while the research record retains the eventual target and target MAE.
    data.iloc[11, data.columns.get_loc("Low")] = 99
    data.iloc[11, data.columns.get_loc("High")] = 106
    data.iloc[16, data.columns.get_loc("High")] = 116
    result = TradePlanningReplayEngine(TargetKnownDetector()).replay(
        data,
        symbol="TEST",
        timeframe="1D",
        entry_policies=(ReplayEntryPolicy.PROXIMAL,),
        stop_policies=(ReplayStopPolicy("ZW10", zone_width_fraction=0.1),),
    )
    demand = next(item for item in result.observations if item.zone_type == "DEMAND")
    assert demand.outcome == ReplayOutcome.STOP_BEFORE_TARGET
    assert demand.first_stop_index == 11
    assert demand.first_target_index == 16
    assert demand.mae_before_target_price is not None


def test_final_stop_families_and_replay_horizons_are_complete() -> None:
    assert [item.zone_width_fraction for item in ZONE_WIDTH_STOP_POLICIES] == [
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
    ]
    assert [item.atr_fraction for item in ATR_STOP_POLICIES] == [
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
    ]
    assert REPLAY_HORIZON_V1 == {
        "15m": 80,
        "75m": 48,
        "125m": 48,
        "1D": 80,
        "1W": 52,
    }
