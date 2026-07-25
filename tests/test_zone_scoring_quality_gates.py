from backend.engines.zone_scoring_engine.zone_scoring_engine import ZoneScoringEngine
from backend.models.zone import Zone, ZoneType


def _score(strength: float) -> float:
    zone = Zone(
        zone_type=ZoneType.DEMAND,
        upper_price=105,
        lower_price=100,
        created_index=10,
        strength=strength,
        is_fresh=True,
        touch_count=0,
        merged_count=15,
    )
    return ZoneScoringEngine().score([zone]).scored_zones[0].total_score


def test_weak_departure_cannot_become_moderate_from_freshness() -> None:
    assert _score(17.0) <= 49


def test_limited_departure_is_rejected_even_with_other_points() -> None:
    assert _score(10.0) <= 39


def test_strong_label_requires_strong_departure() -> None:
    assert _score(25.0) <= 69


def test_elite_label_requires_near_maximum_departure() -> None:
    assert _score(30.0) <= 84
