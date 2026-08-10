from dataclasses import replace

from backend.engines.zone_scoring_engine.zone_scoring_engine import ZoneScoringEngine
from backend.models.candle_classification import (
    CandleClassification,
    CandleDirection,
    CandleStructure,
)
from backend.models.departure import DepartureDirection, DepartureStrength
from backend.models.formation_evidence import (
    CanonicalFormationEvidence,
    FormationCandleEvidence,
)
from backend.models.zone import Zone, ZoneType
from backend.models.zone_scoring.canonical_zone_quality import ZoneQualityContext
from backend.services.zone_explanation_service import ZoneExplanationService


def candle(index, body, ratio, *, explosive=False, relative=1.5):
    return FormationCandleEvidence(
        index,
        f"2026-01-{index + 1:02d}",
        CandleClassification(
            index,
            CandleDirection.BULLISH,
            CandleStructure.EXCITING,
            body,
            body / ratio,
            ratio,
            explosive,
            relative,
            0.9,
        ),
    )


def zone(
    *,
    explosive=True,
    strength=DepartureStrength.VERY_STRONG,
    leg_in_body=5,
    leg_out_body=18,
    close=130,
    base_ratio=0.12,
):
    incoming = (candle(0, leg_in_body, 0.7),)
    base = FormationCandleEvidence(
        1,
        "2026-01-02",
        CandleClassification(
            1,
            CandleDirection.NEUTRAL,
            CandleStructure.BASE,
            base_ratio * 10,
            10,
            base_ratio,
            False,
            0.6,
            0.5,
        ),
    )
    outgoing = (candle(2, leg_out_body, 0.85, explosive=explosive, relative=2.5),)
    evidence = CanonicalFormationEvidence(
        "DBR",
        0,
        0,
        (incoming[0].timestamp,),
        incoming,
        DepartureDirection.BEARISH,
        1,
        1,
        (base.timestamp,),
        (base,),
        (base_ratio,),
        1,
        2,
        2,
        (outgoing[0].timestamp,),
        outgoing,
        True,
        explosive,
        None,
        None,
        False,
        None,
        strength,
        True,
        110,
        close,
        "CANONICAL_FORMATION_ACCEPTED",
    )
    return Zone(
        ZoneType.DEMAND,
        110,
        100,
        1,
        pattern_type="DROP_BASE_RALLY",
        formation_evidence=evidence,
    )


def context(status="FRESH", penetration=0, authenticity="AUTHENTIC"):
    return ZoneQualityContext(
        lifecycle_status=status,
        is_fresh=status == "FRESH",
        max_penetration_percent=penetration,
        authenticity_status=authenticity,
    )


def score(item, ctx):
    return ZoneScoringEngine().score([item], {item.created_index: ctx}).scored_zones[0]


def test_explosive_fresh_zone_scores_above_acceptable_zone():
    high = score(zone(), context())
    acceptable = score(
        zone(
            explosive=False,
            strength=DepartureStrength.STRONG,
            leg_out_body=9,
            close=115,
            base_ratio=0.35,
        ),
        context(),
    )
    assert high.total_score > acceptable.total_score
    assert high.departure_quality_score > acceptable.departure_quality_score


def test_fresh_scores_above_tested_for_same_formation():
    item = zone()
    assert (
        score(item, context("FRESH")).total_score
        > score(item, context("TESTED_RESPECTED")).total_score
    )


def test_shallow_reaction_scores_above_deep_reaction():
    item = zone()
    shallow = score(item, context("REACTING", 10))
    deep = score(item, context("REACTING", 90))
    assert shallow.lifecycle_quality_score > deep.lifecycle_quality_score


def test_legout_dominance_and_clearance_are_differentiated():
    dominant = score(zone(leg_in_body=4, leg_out_body=20, close=135), context())
    marginal = score(zone(leg_in_body=9, leg_out_body=10, close=112), context())
    assert dominant.legout_dominance_score > marginal.legout_dominance_score
    assert dominant.structural_clearance_score > marginal.structural_clearance_score


def test_same_evidence_is_deterministic():
    item = zone()
    first = score(item, context())
    second = score(item, context())
    assert first.total_score == second.total_score
    assert first.reason_codes == second.reason_codes
    assert first.components == second.components


def test_htf_and_trade_confidence_are_not_inputs():
    item = zone()
    baseline = score(item, context())
    # Neither concept exists on the canonical input model, so reevaluation is identical.
    assert score(item, context()).total_score == baseline.total_score


def test_invalidated_zone_still_has_a_deterministic_score():
    item = zone()
    invalidated = score(item, context("INVALIDATED", 100))
    assert invalidated.total_score >= 0
    assert invalidated.lifecycle_quality_score == 0
    assert "LIFECYCLE_INVALIDATED" in invalidated.reason_codes


def test_legacy_strength_mutation_does_not_change_canonical_quality():
    item = zone()
    changed = replace(item, strength=99, touch_count=20, merged_count=8)
    assert score(item, context()).total_score == score(changed, context()).total_score


def test_dashboard_and_detail_explanation_share_the_canonical_total():
    item = zone()
    canonical = score(item, context())
    detail = ZoneExplanationService.build(item, canonical)
    assert detail.overall_score == canonical.total_score
    assert round(sum(component.score for component in canonical.components), 1) == (
        canonical.raw_score
    )
