"""Regression locks for frozen Leg-In structural shadow datasets."""

import json
from pathlib import Path

import pytest


FIXTURE_DIR = Path("tests/fixtures/leg_in_structural")


@pytest.mark.parametrize(
    ("name", "symbols", "zones"),
    [
        ("daily_nse500.json", 500, 932),
        ("weekly_nifty100.json", 100, 21),
        ("minute_15_nifty50.json", 50, 1125),
        ("minute_75_nifty50.json", 50, 236),
        ("minute_125_nifty50.json", 50, 162),
    ],
)
def test_frozen_dataset_counts(name: str, symbols: int, zones: int) -> None:
    payload = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))

    assert payload["audit_only"] is True
    assert payload["production_gate_active"] is False
    assert payload["symbols_processed"] == symbols
    assert payload["canonical_zones"] == zones
    assert sum(payload["patterns"].values()) == zones
    assert sum(payload["zone_types"].values()) == zones
    assert payload["one_candle_leg_ins"] + payload["multi_candle_leg_ins"] == zones
    assert sum(payload["structural_states"].values()) == zones


def test_sonacoms_forensic_fixture_is_congested_but_still_visible() -> None:
    payload = json.loads(
        (FIXTURE_DIR / "daily_nse500.json").read_text(encoding="utf-8")
    )
    matches = [
        item
        for item in payload["records"]
        if item["symbol"] == "SONACOMS"
        and abs(item["proximal"] - 720.5) < 0.02
        and abs(item["distal"] - 707.0) < 0.02
    ]

    assert len(matches) == 1
    zone = matches[0]
    assert zone["structural_state"] == "CONGESTED"
    assert zone["dashboard_visible"] is True
    assert zone["pause_candle_count"] == 1
    assert zone["prior_zone_occupancy_ratio"] == 1.0
    assert "APPROACH_HIGH_OCCUPANCY" in zone["reason_codes"]
    assert "APPROACH_HIGH_OVERLAP" in zone["reason_codes"]


def test_combined_study_is_shadow_only_and_complete() -> None:
    payload = json.loads(
        (FIXTURE_DIR / "multitimeframe_summary.json").read_text(encoding="utf-8")
    )

    assert payload["audit_only"] is True
    assert payload["production_gate_active"] is False
    expected = payload["combined"]["canonical_zones"]
    assert expected == sum(item["canonical_zones"] for item in payload["datasets"])
    assert len(payload["threshold_study"]) == 10
    for impact in payload["threshold_study"].values():
        assert impact["retained"] + impact["rejected"] == expected
        assert impact["dashboard_retained"] + impact["dashboard_rejected"] == (
            payload["combined"]["dashboard_visible"]
        )


def test_review_packet_is_stratified_and_contains_required_cases() -> None:
    payload = json.loads(
        (FIXTURE_DIR / "labelled_review_packet.json").read_text(encoding="utf-8")
    )

    assert payload["summary"]["review_count"] == 250
    assert payload["summary"]["label_distribution"] == {
        "PENDING_HUMAN_REVIEW": 250
    }
    symbols = {item["evidence"]["symbol"] for item in payload["reviews"]}
    assert {"BLS", "SONACOMS"} <= symbols
