"""Regression locks for Pre-Milestone 7D batch shadow enrichment."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from backend.api import scanner
from backend.api.models.scanner_response import ZoneResearchResultResponse


def row(**changes: object) -> ZoneResearchResultResponse:
    values = {
        "symbol": "TCS",
        "timeframe": "1D",
        "zone_type": "DEMAND",
        "proximal_price": 100.0,
        "distal_price": 95.0,
        "zone_score": 80.0,
        "zone_id": "TCS:1D:DZ1",
        "pattern_type": "RBR",
    }
    values.update(changes)
    return ZoneResearchResultResponse.model_construct(**values)


def canonical_payload() -> dict[str, object]:
    return {
        "combined_context": {"state": "fixture"},
        "canonical_analysis": {
            "canonical_trend": {},
            "htf_location": {},
            "trend_alignment": "ALIGNED",
            "trend_timeframe": "1W",
            "location_timeframe": "1M",
            "location_relationship": "FULL_OVERLAP",
            "location_compatibility": "ALIGNED",
            "data_sufficient": True,
            "reason_codes": ["FIXTURE"],
        },
    }


def test_scanner_row_trade_confidence_equals_direct_engine(monkeypatch) -> None:
    monkeypatch.setattr(
        scanner._timeframe_confluence,
        "build",
        Mock(return_value=canonical_payload()),
    )
    item = row()

    serialized = scanner._canonical_trade_confidence_for_row(
        item, refresh_key="snapshot-1"
    )

    assert serialized.score == 92.0
    assert serialized.label == "VERY_HIGH"
    assert serialized.data_sufficiency == "AVAILABLE"
    assert serialized.shadow_mode is False


def test_context_failure_isolated_by_batch_contract(monkeypatch) -> None:
    build = Mock(side_effect=RuntimeError("provider unavailable"))
    monkeypatch.setattr(scanner._timeframe_confluence, "build", build)

    try:
        scanner._canonical_trade_confidence_for_row(row(), refresh_key="snapshot-2")
    except RuntimeError as error:
        assert str(error) == "provider unavailable"

    # The helper raises so the scanner's per-row enrichment boundary can retain
    # the row with trade_confidence=None rather than fail the universe scan.
    assert build.call_count == 1


def test_frontend_has_no_per_row_confluence_request() -> None:
    source = Path(
        "frontend/src/components/scanner/ScannerResultsTable.tsx"
    ).read_text(encoding="utf-8")
    assert "getTimeframeConfluence" not in source
    assert "result.trade_confidence" in source


def test_trade_confidence_response_field_is_shadow_only() -> None:
    confidence = SimpleNamespace(
        total_score=50.0,
        label=SimpleNamespace(value="MODERATE"),
        zone_quality_score=50.0,
        zone_quality_contribution=20.0,
        location_contribution=17.5,
        trend_contribution=12.5,
        location_alignment="NO_HTF_CONTEXT",
        trend_alignment="UNKNOWN",
        combined_context="INSUFFICIENT_CONTEXT",
        htf_overlap_type="NO_OVERLAP",
        htf_direction_compatibility="NO_HTF_CONTEXT",
        data_sufficiency=SimpleNamespace(value="INSUFFICIENT"),
        reason_codes=("FIXTURE",),
        evidence=("fixture",),
    )
    response = scanner._serialize_trade_confidence(confidence)
    assert response.shadow_mode is False
    assert response.score == 50.0


def test_scanner_row_enrichment_uses_pydantic_copy() -> None:
    original = row()
    confidence = scanner.CanonicalTradeConfidenceResponse(
        score=50,
        label="MODERATE",
        zone_quality_score=50,
        zone_quality_contribution=20,
        location_contribution=17.5,
        trend_contribution=12.5,
        location_alignment="NO_HTF_CONTEXT",
        trend_alignment="UNKNOWN",
        combined_context="INSUFFICIENT_CONTEXT",
        htf_overlap_type="NO_OVERLAP",
        htf_direction_compatibility="NO_HTF_CONTEXT",
        data_sufficiency="INSUFFICIENT",
    )
    enriched = original.model_copy(update={"trade_confidence": confidence})
    assert original.trade_confidence is None
    assert enriched.trade_confidence == confidence
