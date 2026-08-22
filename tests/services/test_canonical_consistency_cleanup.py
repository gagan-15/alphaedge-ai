"""Regression guards for the pre-Trade-Confidence consistency cleanup."""

from pathlib import Path

from backend.models.departure import DepartureDirection, DepartureStrength
from backend.models.formation_evidence import CanonicalFormationEvidence
from backend.models.zone import Zone, ZoneType
from backend.services.scanner.canonical_zone_analysis_service import (
    CanonicalZoneAnalysisService,
)


def _evidence() -> CanonicalFormationEvidence:
    return CanonicalFormationEvidence(
        pattern="RALLY_BASE_RALLY",
        leg_in_start_index=0,
        leg_in_end_index=0,
        leg_in_timestamps=("2026-01-01",),
        leg_in_candles=(),
        leg_in_direction=DepartureDirection.BULLISH,
        base_start_index=1,
        base_end_index=1,
        base_timestamps=("2026-01-02",),
        base_candles=(),
        base_body_ratios=(0.2,),
        base_candle_count=1,
        leg_out_start_index=2,
        leg_out_end_index=2,
        leg_out_timestamps=("2026-01-03",),
        leg_out_candles=(),
        first_leg_out_exciting=True,
        first_leg_out_explosive=True,
        second_leg_out_exciting=None,
        second_leg_out_explosive=None,
        significant_gap=True,
        gap_measurement=2.5,
        departure_strength=DepartureStrength.STRONG,
        closing_rule_passed=True,
        closing_comparison_reference=100.0,
        qualifying_close=105.0,
        acceptance_reason="Canonical formation accepted.",
    )


def test_canonical_analysis_preserves_existing_engine_objects() -> None:
    evidence = _evidence()
    zone = Zone(
        ZoneType.DEMAND,
        upper_price=102.0,
        lower_price=98.0,
        created_index=1,
        pattern_type="RALLY_BASE_RALLY",
        formation_evidence=evidence,
    )
    lifecycle, authenticity, quality, trend, htf = (object() for _ in range(5))

    result = CanonicalZoneAnalysisService.compose(
        zone=zone,
        zone_id="TCS:1D:1",
        symbol="tcs",
        timeframe="1D",
        lifecycle=lifecycle,
        authenticity=authenticity,
        zone_quality=quality,
        canonical_trend=trend,
        htf_context=htf,
        alignment="ALIGNED",
        trend_timeframe="1W",
        location_timeframe="1M",
        location_relationship="FULL_OVERLAP",
        location_compatibility="ALIGNED",
        combined_context={"result": "ALIGNED"},
        data_sufficient=True,
        reason_codes=("CANONICAL_GTF_TREND", "HTF_FULL_OVERLAP_ALIGNED"),
    )

    assert result.formation_evidence is evidence
    assert result.lifecycle is lifecycle
    assert result.authenticity is authenticity
    assert result.zone_quality is quality
    assert result.canonical_trend is trend
    assert result.htf_context is htf
    assert result.proximal == 102.0
    assert result.distal == 98.0
    assert result.significant_gap is True
    assert result.gap_measurement == 2.5
    assert result.trend_timeframe == "1W"
    assert result.location_timeframe == "1M"
    assert result.location_relationship == "FULL_OVERLAP"
    assert result.location_compatibility == "ALIGNED"
    assert result.data_sufficient is True


def test_production_scanner_does_not_call_legacy_measurement_helpers() -> None:
    source = Path("backend/api/scanner.py").read_text(encoding="utf-8")

    assert source.count("_measure_zone(") == 1
    assert source.count("_departure_gap(") == 1
    assert source.count("_is_zone_invalidated(") == 1
    assert source.count("_has_completed_test(") == 1


def test_frontend_lifecycle_uses_canonical_response_fields() -> None:
    source = Path(
        "frontend/src/components/scanner/stockZoneAnalysis.ts"
    ).read_text(encoding="utf-8")

    assert "result.test_count ?? result.touch_count" in source
    assert 'result.lifecycle_status === "INVALIDATED"' in source
    assert "later wick intersection(s)" not in source
    assert "function trend(" not in source
