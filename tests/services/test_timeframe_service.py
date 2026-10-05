"""Frozen deterministic EOD aggregation semantics."""

import pandas as pd

from backend.services.market_data.timeframe_service import aggregate_timeframe


def source() -> pd.DataFrame:
    index = pd.to_datetime([
        "2026-01-29", "2026-01-30", "2026-02-02", "2026-02-03"
    ])
    return pd.DataFrame(
        {
            "Open": [10, 11, 20, 21],
            "High": [12, 14, 24, 23],
            "Low": [9, 10, 19, 20],
            "Close": [11, 13, 22, 21],
            "Volume": [100, 200, 300, 400],
        },
        index=index,
    )


def test_weekly_uses_friday_boundary_and_includes_current_bucket() -> None:
    weekly = aggregate_timeframe(source(), "1W")
    assert list(weekly.index) == list(pd.to_datetime(["2026-01-30", "2026-02-06"]))
    assert weekly.iloc[0].to_dict() == {
        "Open": 10, "High": 14, "Low": 9, "Close": 13, "Volume": 300
    }
    assert weekly.iloc[1].to_dict() == {
        "Open": 20, "High": 24, "Low": 19, "Close": 21, "Volume": 700
    }


def test_monthly_uses_calendar_boundary_without_interpolation() -> None:
    monthly = aggregate_timeframe(source(), "1M")
    assert list(monthly.index) == list(pd.to_datetime(["2026-01-31", "2026-02-28"]))
    assert monthly["Volume"].tolist() == [300, 700]
