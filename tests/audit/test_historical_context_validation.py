"""Milestone 9B point-in-time and leakage regression tests."""

from __future__ import annotations

import pandas as pd
import pytest

from backend.research.historical_context_validation import (
    HistoricalContextReconstructor,
)


def _history(periods: int = 8) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=periods, freq="D")
    return pd.DataFrame(
        {
            "Open": range(100, 100 + periods),
            "High": range(102, 102 + periods),
            "Low": range(99, 99 + periods),
            "Close": range(101, 101 + periods),
            "Volume": [1_000] * periods,
        },
        index=index,
    )


@pytest.mark.parametrize(
    "dependency",
    [
        "execution candles",
        "higher-timeframe candles",
        "trend candles",
        "opposing-zone source candles",
        "lifecycle source candles",
        "authenticity source candles",
        "forward outcomes",
    ],
)
def test_future_data_cannot_enter_a_historical_prefix(dependency: str) -> None:
    """Every Milestone 9B dependency is sealed at the planning timestamp."""

    del dependency  # The same canonical prefix boundary applies to every source.
    original = _history()
    cutoff = original.index[4]
    future = pd.DataFrame(
        {
            "Open": [9_999],
            "High": [10_000],
            "Low": [1],
            "Close": [5_000],
            "Volume": [99_999_999],
        },
        index=[cutoff + pd.Timedelta(days=100)],
    )

    before = HistoricalContextReconstructor.prefix(original, cutoff)
    after = HistoricalContextReconstructor.prefix(
        pd.concat([original, future]), cutoff
    )

    pd.testing.assert_frame_equal(before, after, check_freq=False)
    assert after.index.max() == cutoff


def test_prefix_returns_a_copy_and_cannot_mutate_source_history() -> None:
    source = _history()
    prefix = HistoricalContextReconstructor.prefix(source, source.index[3])

    prefix.iloc[0, prefix.columns.get_loc("Close")] = -1

    assert source.iloc[0]["Close"] == 101


def test_empty_or_missing_history_is_honestly_unavailable() -> None:
    cutoff = pd.Timestamp("2024-01-01")

    assert HistoricalContextReconstructor.prefix(None, cutoff).empty
    assert HistoricalContextReconstructor.prefix(pd.DataFrame(), cutoff).empty
