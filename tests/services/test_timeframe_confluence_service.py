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
