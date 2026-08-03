"""Milestone 1.3 canonical formation and regression tests."""

import pandas as pd
import pytest

from backend.engines.demand_supply_engine.base_detector import BaseDetector
from backend.engines.demand_supply_engine.departure_detector import DepartureDetector
from backend.engines.demand_supply_engine.leg_detector import LegDetector
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.models.base_region import BaseRegion
from backend.models.departure import DepartureDirection, DepartureStrength
from tests.fixtures.canonical_formation_cases import (
    CANONICAL_ACCEPTED,
    FORMATION_CASES,
    LEGACY_ACCEPTED,
)


def _frame(rows: list[tuple[float, float, float, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"])


def test_base_detector_uses_complete_group_and_rejects_boundary_candle() -> None:
    data = _frame(
        [
            (10, 12, 8, 11),
            (10, 12, 8, 10.5),
            (10, 12, 8, 10),
            (10, 14, 8, 13),
        ]
    )

    bases = BaseDetector().detect(data)

    assert bases == [BaseRegion(0, 2)]


def test_base_detector_exposes_four_and_five_candle_conditional_candidates() -> None:
    data = _frame([(10, 12, 8, 10.5)] * 5 + [(10, 15, 9, 15)])

    assert BaseDetector().detect(data) == [BaseRegion(0, 4)]


def test_more_than_five_consecutive_base_candles_are_rejected() -> None:
    data = _frame([(10, 12, 8, 10.5)] * 6 + [(10, 15, 9, 15)])

    assert BaseDetector().detect(data) == []


def test_leg_in_and_leg_out_are_maximal_contiguous_sequences() -> None:
    data = _frame(
        [
            (100, 101, 92, 93),
            (93, 94, 85, 86),
            (86, 88, 84, 85.5),
            (85.5, 99, 85, 98),
            (98, 111, 97, 110),
            (110, 112, 108, 110.5),
        ]
    )
    base = BaseRegion(2, 2)

    leg_in = LegDetector().detect_leg_in(data, base)
    leg_out = LegDetector().detect_leg_out(data, base)

    assert leg_in is not None and (leg_in.start_index, leg_in.end_index) == (0, 1)
    assert leg_in.direction == DepartureDirection.BEARISH
    assert leg_out is not None and (leg_out.start_index, leg_out.end_index) == (3, 4)
    assert leg_out.direction == DepartureDirection.BULLISH


@pytest.mark.parametrize(
    ("case", "pattern"),
    [
        ("dbr_strong", "DROP_BASE_RALLY"),
        ("rbr_strong", "RALLY_BASE_RALLY"),
        ("rbd_strong", "RALLY_BASE_DROP"),
        ("dbd_strong", "DROP_BASE_DROP"),
    ],
)
def test_all_four_canonical_patterns(case: str, pattern: str) -> None:
    zones = ZoneDetectionEngine().detect_zones(FORMATION_CASES[case])

    assert len(zones) == 1
    assert zones[0].pattern_type == pattern


def test_single_exciting_candle_is_classified_as_weak_departure() -> None:
    data = FORMATION_CASES["weak_single_departure"]
    base = BaseDetector().detect(data)[0]

    departure = DepartureDetector().detect(data, base)

    assert departure is not None
    assert departure.strength == DepartureStrength.WEAK


def test_exact_boundary_candle_cannot_form_a_zone() -> None:
    assert (
        ZoneDetectionEngine().detect_zones(FORMATION_CASES["boundary_50_percent"])
        == []
    )


def test_zone_boundary_remains_wick_to_wick() -> None:
    data = FORMATION_CASES["dbr_strong"]

    zone = ZoneDetectionEngine().detect_zones(data)[0]

    assert zone.lower_price == 91.0
    assert zone.upper_price == 94.0


def test_leg_out_must_be_stronger_than_complete_leg_in() -> None:
    data = _frame(
        [
            (100, 111, 99, 110),
            (110, 112, 109, 110.5),
            (110.5, 119, 110, 118),
            (118, 120, 117, 119),
        ]
    )
    base = BaseRegion(1, 1)

    departure, rules = DepartureDetector().diagnose(data, base)

    assert departure is None
    result = next(rule for rule in rules if rule["key"] == "leg_out_vs_leg_in")
    assert result["passed"] is False


def test_four_candle_base_is_accepted_with_very_strong_departure() -> None:
    data = FORMATION_CASES["four_base_very_strong_gap"]
    base = BaseDetector().detect(data)[0]

    departure = DepartureDetector().detect(data, base)
    zones = ZoneDetectionEngine().detect_zones(data)

    assert departure is not None
    assert departure.strength == DepartureStrength.VERY_STRONG
    assert len(zones) == 1


def test_frozen_legacy_to_canonical_comparison() -> None:
    actual: set[tuple[str, str, int]] = set()
    detector = ZoneDetectionEngine()
    base_detector = BaseDetector()
    for case, data in FORMATION_CASES.items():
        base_counts = {
            base.end_index: base.candle_count for base in base_detector.detect(data)
        }
        for zone in detector.detect_zones(data):
            actual.add((case, zone.pattern_type, base_counts[zone.created_index]))

    assert actual == CANONICAL_ACCEPTED
    assert CANONICAL_ACCEPTED - LEGACY_ACCEPTED == {
        ("four_base_very_strong_gap", "DROP_BASE_RALLY", 4)
    }
    assert LEGACY_ACCEPTED - CANONICAL_ACCEPTED == {
        ("boundary_50_percent", "DROP_BASE_RALLY", 1)
    }
