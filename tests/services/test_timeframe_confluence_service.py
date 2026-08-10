from backend.services.scanner.timeframe_confluence_service import (
    TimeframeConfluenceService,
)


def test_only_returns_timeframes_above_execution_timeframe() -> None:
    assert TimeframeConfluenceService.higher_timeframes("1D") == (
        "1W",
        "1M",
        "3M",
        "6M",
        "1Y",
    )
    assert TimeframeConfluenceService.higher_timeframes("1W") == (
        "1M",
        "3M",
        "6M",
        "1Y",
    )
    assert TimeframeConfluenceService.higher_timeframes("1Y") == ()


def test_overlap_is_measured_against_selected_execution_zone() -> None:
    assert TimeframeConfluenceService.overlap_percent(100, 110, 105, 115) == 50
    assert TimeframeConfluenceService.overlap_percent(100, 110, 90, 120) == 100
    assert TimeframeConfluenceService.overlap_percent(100, 110, 120, 130) == 0


def test_overlap_relationships_are_tick_size_aware() -> None:
    classify = TimeframeConfluenceService.overlap_relationship
    assert classify(100, 110, 95, 115) == "FULL_OVERLAP"
    assert classify(100, 110, 105, 115) == "PARTIAL_OVERLAP"
    assert classify(100, 110, 110.05, 120, tick_size=0.05) == "TOUCHING"
    assert classify(100, 110, 110.06, 120, tick_size=0.05) == "NO_OVERLAP"


def test_distance_is_zero_for_overlapping_zones() -> None:
    assert TimeframeConfluenceService.distance_percent(
        100,
        110,
        105,
        115,
        100,
    ) == 0
    assert TimeframeConfluenceService.distance_percent(
        100,
        110,
        120,
        130,
        100,
    ) == 10


def test_status_requires_matching_zone_direction() -> None:
    assert TimeframeConfluenceService.status(True, 75, 0) == "CONFIRMED"
    assert TimeframeConfluenceService.status(True, 20, 0) == "PARTIAL"
    assert TimeframeConfluenceService.status(True, 0, 4) == "PARTIAL"
    assert TimeframeConfluenceService.status(False, 100, 0) == "NOT_CONFIRMED"


def test_directional_compatibility_is_independent_of_geometry() -> None:
    classify = TimeframeConfluenceService.compatibility
    assert classify("DEMAND", "DEMAND") == "ALIGNED"
    assert classify("SUPPLY", "SUPPLY") == "ALIGNED"
    assert classify("DEMAND", "SUPPLY") == "OPPOSING"
    assert classify("SUPPLY", "DEMAND") == "OPPOSING"
    assert classify("DEMAND", None) == "NO_HTF_CONTEXT"


def test_reason_codes_are_deterministic() -> None:
    reason = TimeframeConfluenceService.reason_code
    assert reason("FULL_OVERLAP", "ALIGNED") == "HTF_FULL_OVERLAP_ALIGNED"
    assert reason("PARTIAL_OVERLAP", "OPPOSING") == "HTF_PARTIAL_OVERLAP_OPPOSING"
    assert reason("TOUCHING", "ALIGNED") == "HTF_TOUCHING_ALIGNED"
    assert reason("NO_OVERLAP", "ALIGNED") == "HTF_NO_OVERLAP"
    assert reason("NO_OVERLAP", "NO_HTF_CONTEXT") == "HTF_CONTEXT_UNAVAILABLE"
