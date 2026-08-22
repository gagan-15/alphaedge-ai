"""Milestone 10D current-zone comparable historical evidence locks."""

from fastapi.testclient import TestClient

from backend.api.app import app
from backend.historical_evidence.constants import HISTORICAL_EVIDENCE_VERSION

client = TestClient(app)


def comparable(**overrides):
    params = {
        "zone_id": "CURRENT-DZ1",
        "timeframe": "1D",
        "zone_type": "DEMAND",
        "pattern": "DBR",
        "zone_quality_label": "GOOD",
        "trade_confidence_label": "HIGH",
        "current_methodology_version": "formation-1.1",
        **overrides,
    }
    return client.get("/historical-evidence/comparable-zone", params=params)


def test_level_1_uses_exact_cohort_and_preserves_denominators() -> None:
    response = comparable()
    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_match_level"] == 1
    assert payload["exact_level_1"] == {"historical_zones": 103, "interacted_zones": 77}
    assert payload["selected_cohort"] == payload["exact_level_1"]
    summary = payload["summary_metrics"]
    assert summary["interaction_rate"]["denominator"] == summary["historical_zones"]
    assert summary["reaction_2_zone_width"]["denominator"] == summary[
        "interacted_zones"
    ]
    assert summary["structural_target_achievement"]["denominator"] == summary[
        "structural_target_availability"
    ]["numerator"]


def test_level_2_broadens_pattern_only() -> None:
    payload = comparable(zone_quality_label="AVERAGE").json()
    assert payload["selected_match_level"] == 2
    assert payload["exact_level_1"] == {"historical_zones": 22, "interacted_zones": 13}
    assert payload["selected_cohort"] == {
        "historical_zones": 47,
        "interacted_zones": 30,
    }
    assert "pattern" not in payload["applied_cohort_definition"]


def test_level_3_broadens_zone_quality_only_after_narrower_levels() -> None:
    payload = comparable(
        zone_quality_label="STRONG", trade_confidence_label="MODERATE"
    ).json()
    assert payload["selected_match_level"] == 3
    assert payload["exact_level_1"] == {"historical_zones": 1, "interacted_zones": 0}
    assert payload["selected_cohort"] == {
        "historical_zones": 4544,
        "interacted_zones": 3646,
    }
    assert set(payload["applied_cohort_definition"]) == {
        "timeframe",
        "zone_type",
        "trade_confidence_label",
    }


def test_level_3_insufficient_is_returned_without_crossing_confidence() -> None:
    payload = comparable(
        zone_type="SUPPLY", pattern="DBD", zone_quality_label="GOOD"
    ).json()
    assert payload["selected_match_level"] == 3
    assert payload["selected_cohort"] == {
        "historical_zones": 19,
        "interacted_zones": 16,
    }
    assert payload["reliability"] == "INSUFFICIENT"
    assert payload["applied_cohort_definition"]["trade_confidence_label"] == "HIGH"


def test_very_high_and_unsupported_timeframe_are_explicit() -> None:
    very_high = comparable(trade_confidence_label="VERY_HIGH").json()
    assert very_high["status"] == "NO_COMPARABLE_HISTORICAL_EVIDENCE"
    assert "No historical VERY_HIGH observations" in very_high["explanation"]
    unsupported = comparable(timeframe="75m").json()
    assert unsupported["status"] == "UNSUPPORTED_TIMEFRAME"
    assert "Daily and Weekly" in unsupported["explanation"]


def test_empty_level_3_cohort_is_explicit() -> None:
    payload = comparable(timeframe="1W", trade_confidence_label="HIGH").json()
    assert payload["status"] == "NO_COMPARABLE_HISTORICAL_EVIDENCE"
    assert payload["selected_match_level"] == 3
    assert payload["selected_cohort"] == {"historical_zones": 0, "interacted_zones": 0}


def test_weekly_never_uses_daily_and_result_is_deterministic() -> None:
    params = {
        "timeframe": "1W",
        "zone_type": "SUPPLY",
        "pattern": "DBD",
        "zone_quality_label": "AVERAGE",
        "trade_confidence_label": "MODERATE",
    }
    first = comparable(**params).json()
    second = comparable(**params).json()
    assert first == second
    assert first["current_zone"]["timeframe"] == "1W"
    assert first["applied_cohort_definition"]["timeframe"] == "1W"


def test_methodology_and_dataset_versions_are_enforced() -> None:
    mismatch = comparable(current_methodology_version="formation-1.0")
    assert mismatch.status_code == 409
    assert "current methodology version" in mismatch.json()["detail"]
    dataset = comparable(dataset_version="milestone-9c.0")
    assert dataset.status_code == 409


def test_current_zone_does_not_mutate_frozen_population() -> None:
    before = client.get("/historical-evidence/metadata").json()["record_count"]
    comparable(zone_id="NOT-IN-FROZEN-DATASET")
    after = client.get("/historical-evidence/metadata").json()["record_count"]
    assert before == after == 37_725


def test_comparable_path_has_no_provider_or_production_engine_dependency() -> None:
    from pathlib import Path

    source = Path("backend/historical_evidence/service.py").read_text(encoding="utf-8")
    for forbidden in (
        "MarketDataService",
        "ZoneDetectionEngine",
        "CanonicalTradeConfidenceEngine",
        "data_providers",
    ):
        assert forbidden not in source
    assert HISTORICAL_EVIDENCE_VERSION == "milestone-9c.1"
