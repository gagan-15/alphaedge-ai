"""Milestone 10F immutable-cache and aggregation regression locks."""

from backend.historical_evidence.constants import HISTORICAL_EVIDENCE_VERSION
from backend.historical_evidence.service import HistoricalEvidenceService


def test_summary_cache_is_cohort_safe_and_returns_copies() -> None:
    service = HistoricalEvidenceService()
    demand = service.filters(timeframe="1D", zone_type="DEMAND")
    supply = service.filters(timeframe="1D", zone_type="SUPPLY")

    demand_first = service.summary(HISTORICAL_EVIDENCE_VERSION, demand)
    supply_result = service.summary(HISTORICAL_EVIDENCE_VERSION, supply)
    demand_first["historical_zones"] = -1
    demand_second = service.summary(HISTORICAL_EVIDENCE_VERSION, demand)

    assert demand_second["historical_zones"] == 15_652
    assert supply_result["historical_zones"] == 15_221
    assert demand_second["historical_zones"] != supply_result["historical_zones"]


def test_sqlite_native_medians_preserve_frozen_values() -> None:
    service = HistoricalEvidenceService()
    filters = service.filters(
        timeframe="1D",
        zone_type="DEMAND",
        pattern="DBR",
        zone_quality_label="WEAK",
        trade_confidence_label="MODERATE",
    )

    summary = service.summary(HISTORICAL_EVIDENCE_VERSION, filters)

    assert summary["historical_zones"] == 1_567
    assert summary["interacted_zones"] == 1_276
    assert summary["reaction_2_zone_width"] == {
        "numerator": 1_102,
        "denominator": 1_276,
        "percent": 86.36,
    }
    assert summary["structural_target_achievement"] == {
        "numerator": 274,
        "denominator": 413,
        "percent": 66.34,
    }
