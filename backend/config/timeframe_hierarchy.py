"""Canonical, read-only timeframe roles used by chart context features."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeframeHierarchy:
    location: str | None
    trend: str | None
    execution: str


TIMEFRAME_HIERARCHY: dict[str, TimeframeHierarchy] = {
    "5M": TimeframeHierarchy("1H", "15M", "5M"),
    "15M": TimeframeHierarchy("4H", "1H", "15M"),
    "75M": TimeframeHierarchy("1D", "4H", "75M"),
    "125M": TimeframeHierarchy("1D", "4H", "125M"),
    "1H": TimeframeHierarchy("1D", "4H", "1H"),
    "2H": TimeframeHierarchy("1D", "4H", "2H"),
    "4H": TimeframeHierarchy("1W", "1D", "4H"),
    "6H": TimeframeHierarchy("1W", "1D", "6H"),
    "1D": TimeframeHierarchy("1M", "1W", "1D"),
    "1W": TimeframeHierarchy("3M", "1M", "1W"),
    "1M": TimeframeHierarchy("1Y", "3M", "1M"),
    "3M": TimeframeHierarchy("1Y", "6M", "3M"),
    "6M": TimeframeHierarchy(None, "1Y", "6M"),
    "1Y": TimeframeHierarchy(None, None, "1Y"),
}

# Ordering metadata lives beside the canonical hierarchy so consumers never
# maintain their own timeframe lists. Values are comparable duration units;
# calendar periods use stable ordering values rather than trading-bar math.
TIMEFRAME_DURATION_MINUTES: dict[str, int] = {
    "5M": 5,
    "15M": 15,
    "1H": 60,
    "75M": 75,
    "2H": 120,
    "125M": 125,
    "4H": 240,
    "6H": 360,
    "1D": 1_440,
    "1W": 10_080,
    "1M": 43_200,
    "3M": 129_600,
    "6M": 259_200,
    "1Y": 525_600,
}


def get_timeframe_hierarchy(timeframe: str) -> TimeframeHierarchy:
    normalized = timeframe.strip().upper()
    return TIMEFRAME_HIERARCHY.get(
        normalized, TimeframeHierarchy(None, None, normalized)
    )


def is_timeframe_at_or_below(timeframe: str | None, ceiling: str) -> bool:
    """Compare known canonical timeframes without duplicating their order."""

    if timeframe is None:
        return False
    normalized = timeframe.strip().upper()
    normalized_ceiling = ceiling.strip().upper()
    duration = TIMEFRAME_DURATION_MINUTES.get(normalized)
    ceiling_duration = TIMEFRAME_DURATION_MINUTES.get(normalized_ceiling)
    return (
        duration is not None
        and ceiling_duration is not None
        and duration <= ceiling_duration
    )
