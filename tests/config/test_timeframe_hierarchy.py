from backend.config.timeframe_hierarchy import (
    get_timeframe_hierarchy,
    is_timeframe_at_or_below,
)


def test_daily_gtf_roles_are_explicit() -> None:
    roles = get_timeframe_hierarchy("1D")
    assert roles.location == "1M"
    assert roles.trend == "1W"
    assert roles.execution == "1D"


def test_supported_intraday_roles_are_deterministic() -> None:
    assert get_timeframe_hierarchy("5m").trend == "15M"
    assert get_timeframe_hierarchy("75m").location == "1D"
    assert get_timeframe_hierarchy("6h").trend == "1D"


def test_unknown_timeframe_is_safe_and_unavailable() -> None:
    roles = get_timeframe_hierarchy("custom")
    assert roles.location is None
    assert roles.trend is None
    assert roles.execution == "CUSTOM"


def test_execution_timeframes_are_programmatically_at_or_below_weekly() -> None:
    execution_timeframes = (
        "5M",
        "15M",
        "1H",
        "75M",
        "2H",
        "125M",
        "4H",
        "6H",
        "1D",
        "1W",
    )
    assert all(
        is_timeframe_at_or_below(timeframe, "1W")
        for timeframe in execution_timeframes
    )


def test_above_weekly_and_unknown_timeframes_do_not_trigger_execution_policy() -> None:
    assert not is_timeframe_at_or_below("1M", "1W")
    assert not is_timeframe_at_or_below("3M", "1W")
    assert not is_timeframe_at_or_below("CUSTOM", "1W")
    assert not is_timeframe_at_or_below(None, "1W")
