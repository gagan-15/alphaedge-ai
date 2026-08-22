"""Shadow-only canonical Leg-In structural evidence tests."""

from dataclasses import replace

import pandas as pd
import pytest

from backend.engines.demand_supply_engine.leg_in_structural_evidence_engine import (
    LegInStructuralEvidenceEngine,
)
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.models.base_region import BaseRegion
from backend.models.departure import Departure, DepartureDirection
from backend.models.leg_in_structural_evidence import (
    LegInFormationValidity,
    LegInStructuralState,
)
from tests.fixtures.canonical_formation_cases import FORMATION_CASES


def _frame(rows: list[tuple[float, float, float, float]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"], dtype=float)
    frame.index = pd.date_range("2026-01-01", periods=len(frame), freq="D")
    return frame


def _departure(
    direction: DepartureDirection,
    start: int,
    end: int,
) -> Departure:
    return Departure(
        direction=(
            DepartureDirection.BULLISH
            if direction == DepartureDirection.BEARISH
            else DepartureDirection.BEARISH
        ),
        departure_index=end + 2,
        leg_in_direction=direction,
        leg_in_start_index=start,
        leg_in_end_index=end,
    )


@pytest.mark.parametrize(
    ("rows", "direction", "leg_start", "leg_end"),
    [
        (
            [(20, 21, 19, 20)] * 20 + [(18, 18.2, 13, 13.2), (13.2, 14, 12, 13)],
            DepartureDirection.BEARISH,
            20,
            20,
        ),
        (
            [(20, 21, 19, 20)] * 20 + [(13, 18, 12.8, 17.8), (17.8, 18, 17, 17.5)],
            DepartureDirection.BULLISH,
            20,
            20,
        ),
        (
            [(20, 21, 19, 20)] * 20
            + [(20, 20.2, 16, 16.2), (16.2, 16.4, 13, 13.2), (13.2, 14, 12, 13)],
            DepartureDirection.BEARISH,
            20,
            21,
        ),
        (
            [(20, 21, 19, 20)] * 20
            + [(13, 17, 12.8, 16.8), (16.8, 20, 16.6, 19.8), (19.8, 20, 19, 19.5)],
            DepartureDirection.BULLISH,
            20,
            21,
        ),
    ],
)
def test_clean_single_and_multi_candle_directional_approaches(
    rows, direction, leg_start, leg_end
) -> None:
    data = _frame(rows)
    if direction == DepartureDirection.BULLISH:
        data.iloc[19] = (22, 23, 17, 17.2)
    else:
        data.iloc[19] = (12, 18, 11, 17.8)
    evidence = LegInStructuralEvidenceEngine().evaluate(
        data,
        BaseRegion(leg_end + 1, leg_end + 1),
        _departure(direction, leg_start, leg_end),
        proximal=14,
        distal=12,
    )

    assert evidence.leg_in_candle_count == leg_end - leg_start + 1
    assert evidence.directional_displacement > 0
    assert evidence.structural_state in {
        LegInStructuralState.CLEAN,
        LegInStructuralState.ACCEPTABLE,
        LegInStructuralState.BORDERLINE,
    }


def test_one_small_pause_is_allowed_but_second_pause_stops_walk() -> None:
    data = _frame(
        [(30, 31, 29, 30)] * 18
        + [
            (25, 26, 20, 20.5),
            (20.5, 21, 19, 20.2),  # allowed pause
            (20.2, 21, 19.2, 20),  # second pause is not absorbed
            (20, 20.2, 15, 15.2),
            (15.2, 16, 14, 15),
        ]
    )
    evidence = LegInStructuralEvidenceEngine().evaluate(
        data,
        BaseRegion(22, 22),
        _departure(DepartureDirection.BEARISH, 21, 21),
        proximal=16,
        distal=14,
    )

    assert evidence.pause_candle_count == 1
    assert evidence.broader_approach_start_index == 20
    assert evidence.broader_approach_end_index == 21


def test_opposite_impulse_stops_broader_approach() -> None:
    data = _frame(
        [(20, 21, 19, 20)] * 19
        + [
            (14, 19, 13, 18.8),
            (19, 19.2, 14, 14.2),
            (14.2, 14.4, 10, 10.2),
            (10.2, 11, 9, 10),
        ]
    )
    evidence = LegInStructuralEvidenceEngine().evaluate(
        data,
        BaseRegion(22, 22),
        _departure(DepartureDirection.BEARISH, 20, 21),
        proximal=11,
        distal=9,
    )

    assert evidence.broader_approach_start_index == 20


def test_metrics_and_reason_codes_are_deterministic() -> None:
    data = _frame(
        [(30, 32, 28, 30)] * 20 + [(24, 25, 19, 20), (20, 21, 15, 16), (16, 17, 14, 15)]
    )
    data.iloc[19] = (14, 20, 13, 19.8)
    engine = LegInStructuralEvidenceEngine()
    args = (
        data,
        BaseRegion(22, 22),
        _departure(DepartureDirection.BEARISH, 20, 21),
        17,
        14,
    )
    first = engine.evaluate(*args)
    second = engine.evaluate(*args)

    assert first == second
    assert first.directional_displacement == pytest.approx(8)
    assert first.displacement_zone_width_ratio == pytest.approx(8 / 3)
    assert first.displacement_volatility_ratio == pytest.approx(2)
    assert first.directional_efficiency == pytest.approx(1)
    assert first.reason_codes == second.reason_codes


def test_base_is_not_absorbed_and_segment_boundary_stops_walk() -> None:
    data = _frame([(20, 21, 19, 20)] * 20 + [(20, 20.2, 15, 15.2), (15.2, 16, 14, 15)])
    evidence = LegInStructuralEvidenceEngine().evaluate(
        data,
        BaseRegion(21, 21),
        _departure(DepartureDirection.BEARISH, 20, 20),
        proximal=16,
        distal=14,
    )

    assert evidence.broader_approach_end_index < 21
    assert evidence.broader_approach_start_index >= 0


def test_shadow_evidence_does_not_change_zone_identity_or_boundary() -> None:
    zones = ZoneDetectionEngine().detect_zones(FORMATION_CASES["dbr_strong"])
    assert len(zones) == 1
    zone = zones[0]
    evidence = zone.formation_evidence
    assert evidence is not None
    assert evidence.leg_in_structural_evidence is not None

    without_shadow = replace(
        zone, formation_evidence=replace(evidence, leg_in_structural_evidence=None)
    )
    assert (
        zone.created_index,
        zone.pattern_type,
        zone.lower_price,
        zone.upper_price,
    ) == (
        without_shadow.created_index,
        without_shadow.pattern_type,
        without_shadow.lower_price,
        without_shadow.upper_price,
    )


@pytest.mark.parametrize(
    ("direction", "pattern"),
    [
        (DepartureDirection.BEARISH, "DBR"),
        (DepartureDirection.BEARISH, "DBD"),
        (DepartureDirection.BULLISH, "RBR"),
        (DepartureDirection.BULLISH, "RBD"),
    ],
)
def test_clear_congestion_gate_is_direction_and_pattern_symmetric(
    direction, pattern
) -> None:
    validity, reasons = LegInStructuralEvidenceEngine._formation_validity(
        width_ratio=0.0,
        efficiency=0.0,
        pre_leg_in_occupancy=1.0,
        body_overlap=0.58,
        direction_changes=2,
        stop_reason="SECOND_PAUSE_OR_CONGESTION",
    )

    assert pattern in {"DBR", "DBD", "RBR", "RBD"}
    assert direction in {DepartureDirection.BEARISH, DepartureDirection.BULLISH}
    assert validity == LegInFormationValidity.INVALID_CLEAR_CONGESTION
    assert "LEG_IN_INSUFFICIENT_DIRECTIONAL_DISPLACEMENT" in reasons
    assert "LEG_IN_REPEATED_PRE_BASE_ZONE_OCCUPANCY" in reasons


@pytest.mark.parametrize(
    "overrides",
    [
        {"width_ratio": 1.0},  # weak displacement alone is not enough
        {"pre_leg_in_occupancy": 0.0},  # occupancy alone is not enough
        {"body_overlap": 1.0, "pre_leg_in_occupancy": 0.0},
        {
            "efficiency": 0.08,
            "body_overlap": 0.0,
            "direction_changes": 0,
            "stop_reason": "START",
        },
        {"pre_leg_in_occupancy": None},  # insufficient evidence remains eligible
    ],
)
def test_single_or_incomplete_evidence_never_rejects(overrides) -> None:
    values = {
        "width_ratio": 0.0,
        "efficiency": 0.0,
        "pre_leg_in_occupancy": 1.0,
        "body_overlap": 0.0,
        "direction_changes": 0,
        "stop_reason": "START",
    }
    values.update(overrides)

    validity, reasons = LegInStructuralEvidenceEngine._formation_validity(**values)

    assert validity == LegInFormationValidity.VALID
    assert reasons == ()


def test_wick_overlap_is_diagnostic_only() -> None:
    validity, _ = LegInStructuralEvidenceEngine._formation_validity(
        width_ratio=0.0,
        efficiency=0.0,
        pre_leg_in_occupancy=0.0,
        body_overlap=0.0,
        direction_changes=0,
        stop_reason="START",
    )
    assert validity == LegInFormationValidity.VALID


def test_named_frozen_examples_match_v11_expected_results() -> None:
    import json
    from pathlib import Path

    fixture_dir = Path("tests/fixtures/leg_in_structural")
    records = []
    for name in (
        "daily_nse500.json",
        "weekly_nifty100.json",
        "minute_15_nifty50.json",
        "minute_75_nifty50.json",
        "minute_125_nifty50.json",
    ):
        records.extend(json.loads((fixture_dir / name).read_text())["records"])

    def decision(item):
        return LegInStructuralEvidenceEngine._formation_validity(
            width_ratio=item["displacement_zone_width_ratio"],
            efficiency=item["directional_efficiency"],
            pre_leg_in_occupancy=item.get("pre_leg_in_occupancy_ratio"),
            body_overlap=item.get("adjacent_body_overlap_ratio", 0.0),
            direction_changes=item["approach_direction_changes"],
            stop_reason=item["backward_walk_stop_reason"],
        )[0]

    rejected_requirements = (
        ("SONACOMS", "1D", "DBR", 720.5, 707.0),
        ("BLS", "1D", "DBR", 239.8, 236.0),
        ("SCHNEIDER", "1D", "DBR", 1354.8, 1331.0),
        ("AMBER", "1D", "DBD", 7424.0, 7557.0),
        ("ATHERENERG", "1D", "RBR", 1488.0, 1457.0),
        ("NESTLEIND", "125m", "RBR", 1446.1, 1441.0),
    )
    for symbol, timeframe, pattern, proximal, distal in rejected_requirements:
        item = next(
            candidate
            for candidate in records
            if candidate["symbol"] == symbol
            and candidate["timeframe"] == timeframe
            and candidate["pattern"] == pattern
            and abs(candidate["proximal"] - proximal) < 0.02
            and abs(candidate["distal"] - distal) < 0.02
        )
        assert decision(item) == LegInFormationValidity.INVALID_CLEAR_CONGESTION

    survivor_requirements = {
        "AUBANK": ("1D", "DBR", False),
        "CHOICEIN": ("1D", "RBD", False),
        "MAXHEALTH": ("125m", "DBD", True),
        "HINDALCO": ("125m", "RBR", True),
    }
    for symbol, (timeframe, pattern, multi) in survivor_requirements.items():
        candidates = [
            item
            for item in records
            if item["symbol"] == symbol
            and item["timeframe"] == timeframe
            and item["pattern"] == pattern
            and (item["leg_in_candle_count"] > 1) == multi
        ]
        assert candidates, f"Missing frozen regression example: {symbol}"
        assert all(
            decision(item) == LegInFormationValidity.VALID for item in candidates
        )
