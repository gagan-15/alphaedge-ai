"""Deterministic tests for Milestone 7B shadow Trade Confidence."""

from dataclasses import FrozenInstanceError, replace

import pytest

from backend.engines.trade_confidence_engine import CanonicalTradeConfidenceEngine
from backend.models.canonical_trade_confidence import (
    ContextDataSufficiency,
    TradeConfidenceLabel,
)
from backend.models.canonical_zone_analysis import CanonicalZoneAnalysis


def analysis(**changes: object) -> CanonicalZoneAnalysis:
    base = CanonicalZoneAnalysis(
        zone_id="fixture",
        symbol="TCS",
        timeframe="1D",
        zone_type="DEMAND",
        pattern="RBR",
        proximal=100,
        distal=95,
        formation_evidence=None,
        lifecycle=object(),
        authenticity=object(),
        zone_quality=80,
        canonical_trend=object(),
        htf_context=object(),
        alignment="ALIGNED",
        significant_gap=False,
        gap_measurement=None,
        trend_alignment="ALIGNED",
        location_relationship="FULL_OVERLAP",
        location_compatibility="ALIGNED",
        data_sufficient=True,
        reason_codes=("FIXTURE",),
    )
    return replace(base, **changes)


@pytest.mark.parametrize(
    ("relationship", "expected"),
    [
        ("FULL_OVERLAP", 92),
        ("PARTIAL_OVERLAP", 86),
        ("TOUCHING", 80),
        ("NO_OVERLAP", 74.5),
    ],
)
def test_aligned_location_points_are_monotonic(
    relationship: str, expected: float
) -> None:
    result = CanonicalTradeConfidenceEngine.evaluate(
        analysis(location_relationship=relationship)
    )
    assert result.total_score == expected


@pytest.mark.parametrize(
    ("relationship", "expected"),
    [
        ("FULL_OVERLAP", 57),
        ("PARTIAL_OVERLAP", 63),
        ("TOUCHING", 69),
        ("NO_OVERLAP", 74.5),
    ],
)
def test_opposing_location_points(relationship: str, expected: float) -> None:
    result = CanonicalTradeConfidenceEngine.evaluate(
        analysis(location_relationship=relationship, location_compatibility="OPPOSING")
    )
    assert result.total_score == expected
    assert result.label == (
        TradeConfidenceLabel.CONFLICTED
        if relationship != "NO_OVERLAP"
        else TradeConfidenceLabel.HIGH
    )


@pytest.mark.parametrize(
    ("trend", "points"),
    [
        ("ALIGNED", 25),
        ("NEUTRAL", 12.5),
        ("SIDEWAYS", 12.5),
        ("UNKNOWN", 12.5),
        ("UNAVAILABLE", 12.5),
        ("OPPOSING", 0),
    ],
)
def test_trend_normalization(trend: str, points: float) -> None:
    result = CanonicalTradeConfidenceEngine.evaluate(analysis(trend_alignment=trend))
    assert result.trend_contribution == points


def test_opposing_trend_has_conflict_precedence() -> None:
    result = CanonicalTradeConfidenceEngine.evaluate(
        analysis(zone_quality=100, trend_alignment="OPPOSING")
    )
    assert result.total_score == 75
    assert result.label == TradeConfidenceLabel.CONFLICTED


def test_both_unknown_are_insufficient_not_bearish() -> None:
    result = CanonicalTradeConfidenceEngine.evaluate(
        analysis(
            trend_alignment="UNKNOWN",
            alignment="UNKNOWN",
            location_compatibility="NO_HTF_CONTEXT",
            location_relationship="NO_OVERLAP",
        )
    )
    assert result.data_sufficiency == ContextDataSufficiency.INSUFFICIENT
    assert result.label == TradeConfidenceLabel.INSUFFICIENT_CONTEXT
    assert result.location_contribution == 17.5
    assert result.trend_contribution == 12.5


def test_partial_context_caps_very_high_label() -> None:
    result = CanonicalTradeConfidenceEngine.evaluate(
        analysis(zone_quality=100, trend_alignment="UNKNOWN", alignment="UNKNOWN")
    )
    assert result.data_sufficiency == ContextDataSufficiency.PARTIAL
    assert result.total_score == 87.5
    assert result.label == TradeConfidenceLabel.HIGH


def test_same_input_is_deterministic_and_bounded() -> None:
    first = CanonicalTradeConfidenceEngine.evaluate(analysis(zone_quality=150))
    second = CanonicalTradeConfidenceEngine.evaluate(analysis(zone_quality=150))
    assert first == second
    assert 0 <= first.total_score <= 100


def test_canonical_analysis_remains_immutable() -> None:
    value = analysis()
    with pytest.raises(FrozenInstanceError):
        value.zone_quality = 1  # type: ignore[misc]


def test_unrelated_evidence_does_not_change_score() -> None:
    base = CanonicalTradeConfidenceEngine.evaluate(analysis())
    changed = CanonicalTradeConfidenceEngine.evaluate(
        analysis(
            lifecycle={"different": True},
            authenticity={"different": True},
            formation_evidence=None,
            significant_gap=True,
            gap_measurement=99,
        )
    )
    assert base.total_score == changed.total_score
    assert base.label == changed.label
