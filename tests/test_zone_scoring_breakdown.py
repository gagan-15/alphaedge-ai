from backend.engines.zone_scoring_engine.zone_scoring_engine import ZoneScoringEngine
from backend.models.zone import Zone, ZoneType


def test_score_breakdown_matches_raw_and_final_total() -> None:
    zone = Zone(
        zone_type=ZoneType.DEMAND,
        upper_price=105,
        lower_price=100,
        created_index=10,
        strength=25,
        is_fresh=True,
        touch_count=1,
        merged_count=2,
    )

    score = ZoneScoringEngine().score([zone]).scored_zones[0]

    assert score.raw_score == (
        score.freshness_score
        + score.strength_score
        + score.touch_score
        + score.merge_bonus
    )
    assert score.total_score == min(score.raw_score, score.quality_cap, 100)


def test_single_zone_has_no_false_overlap_bonus() -> None:
    zone = Zone(ZoneType.SUPPLY, 110, 100, 10, merged_count=1)

    score = ZoneScoringEngine().score([zone]).scored_zones[0]

    assert score.merge_bonus == 0
