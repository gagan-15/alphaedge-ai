"""Milestone 10B immutable Historical Evidence API regression locks."""

from fastapi.testclient import TestClient

from backend.api.app import app
from backend.historical_evidence.constants import (
    EXPECTED_RECORD_COUNT,
    EXPECTED_TC_COUNTS,
    HISTORICAL_EVIDENCE_VERSION,
)

client = TestClient(app)


def test_metadata_reconciles_frozen_package() -> None:
    response = client.get("/historical-evidence/metadata")
    assert response.status_code == 200
    payload = response.json()
    assert payload["historical_evidence_version"] == HISTORICAL_EVIDENCE_VERSION
    assert payload["record_count"] == EXPECTED_RECORD_COUNT
    assert payload["trade_confidence_counts"] == EXPECTED_TC_COUNTS
    assert len(payload["methodology_fingerprint"]) == 64


def test_summary_reproduces_high_and_moderate_two_zone_width_result() -> None:
    high = client.get(
        "/historical-evidence/summary", params={"trade_confidence_label": "HIGH"}
    ).json()
    moderate = client.get(
        "/historical-evidence/summary", params={"trade_confidence_label": "MODERATE"}
    ).json()
    assert high["historical_zones"] == 270
    assert high["reaction_2_zone_width"] == {
        "numerator": 177,
        "denominator": 189,
        "percent": 93.65,
    }
    assert moderate["historical_zones"] == 7_237
    assert moderate["reaction_2_zone_width"] == {
        "numerator": 4_984,
        "denominator": 5_837,
        "percent": 85.39,
    }
    assert (
        round(
            high["reaction_2_zone_width"]["percent"]
            - moderate["reaction_2_zone_width"]["percent"],
            2,
        )
        == 8.26
    )


def test_very_high_and_empty_cohorts_are_honest() -> None:
    very_high = client.get(
        "/historical-evidence/summary",
        params={"trade_confidence_label": "VERY_HIGH"},
    ).json()
    assert very_high["historical_zones"] == 0
    assert very_high["empty_cohort"] is True
    assert very_high["reaction_2_zone_width"]["percent"] is None
    assert very_high["reliability"] == "INSUFFICIENT"


def test_intraday_timeframes_are_rejected() -> None:
    for timeframe in ("15m", "75m", "125m"):
        response = client.get(
            "/historical-evidence/summary", params={"timeframe": timeframe}
        )
        assert response.status_code == 422
        assert "Daily and Weekly" in response.json()["detail"]


def test_dataset_version_mismatch_is_rejected() -> None:
    response = client.get(
        "/historical-evidence/metadata", params={"dataset_version": "milestone-9c.0"}
    )
    assert response.status_code == 409


def test_filtering_denominators_and_reliability() -> None:
    payload = client.get(
        "/historical-evidence/summary",
        params={"timeframe": "Daily", "zone_type": "demand", "pattern": "DBR"},
    ).json()
    assert payload["historical_zones"] > 0
    assert payload["interaction_rate"]["denominator"] == payload["historical_zones"]
    assert (
        payload["reaction_2_zone_width"]["denominator"] == payload["interacted_zones"]
    )
    assert (
        payload["structural_target_achievement"]["denominator"]
        == payload["structural_target_availability"]["numerator"]
    )
    assert payload["reliability"] in {
        "INSUFFICIENT",
        "EXPLORATORY",
        "MODERATE_EVIDENCE",
        "STRONGER_EVIDENCE",
    }


def test_pagination_and_sorting_are_deterministic() -> None:
    params = {"page": 2, "page_size": 10, "sort_by": "symbol", "sort_direction": "asc"}
    first = client.get("/historical-evidence/zones", params=params)
    second = client.get("/historical-evidence/zones", params=params)
    assert first.status_code == 200
    assert first.json() == second.json()
    payload = first.json()
    assert payload["total"] == EXPECTED_RECORD_COUNT
    assert len(payload["items"]) == 10
    assert payload["page"] == 2


def test_sorting_is_allow_listed() -> None:
    response = client.get(
        "/historical-evidence/zones", params={"sort_by": "drop table historical_zones"}
    )
    assert response.status_code == 422


def test_read_model_does_not_import_production_engines_or_providers() -> None:
    from pathlib import Path

    root = Path("backend/historical_evidence")
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))
    forbidden = (
        "ZoneDetectionEngine",
        "MarketDataService",
        "data_providers",
        "CanonicalTradeConfidenceEngine",
        "CanonicalZoneQualityEngine",
    )
    assert all(name not in source for name in forbidden)
