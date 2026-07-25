"""Tests for modular, trader-readable zone explanations."""

from backend.models.zone import Zone, ZoneType
from backend.models.zone_scoring.zone_score import ZoneScore
from backend.services.zone_explanation_service import ZoneExplanationService


def test_explanation_includes_only_available_measured_factors() -> None:
    zone = Zone(
        zone_type=ZoneType.DEMAND,
        upper_price=105,
        lower_price=100,
        created_index=10,
        strength=30,
        is_fresh=True,
        touch_count=0,
        merged_count=2,
    )
    score = ZoneScore(
        zone=zone,
        freshness_score=30,
        strength_score=30,
        touch_score=20,
        merge_bonus=2,
        total_score=82,
    )

    explanation = ZoneExplanationService.build(zone, score)

    assert explanation.overall_score == 82
    assert explanation.rating == 4
    assert "does not predict" in explanation.summary
    assert {factor.key for factor in explanation.positive_factors} == {
        "freshness",
        "departure",
        "touches",
        "confluence",
    }
    assert explanation.negative_factors == ()


def test_retested_zone_explains_quality_reduction() -> None:
    zone = Zone(
        zone_type=ZoneType.SUPPLY,
        upper_price=105,
        lower_price=100,
        created_index=10,
        is_fresh=False,
        touch_count=4,
    )
    score = ZoneScore(
        zone=zone,
        freshness_score=0,
        strength_score=5,
        touch_score=16,
        merge_bonus=1,
        total_score=22,
    )

    explanation = ZoneExplanationService.build(zone, score)

    assert explanation.label == "Rejected Supply Zone"
    assert {factor.key for factor in explanation.negative_factors} == {
        "freshness",
        "departure",
        "touches",
        "confluence",
    }
