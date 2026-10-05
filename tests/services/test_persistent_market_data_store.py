"""Persistent OHLCV merge and correction regression tests."""

from pathlib import Path

import pandas as pd

from backend.services.market_data.persistent_market_data_store import (
    PersistentMarketDataStore,
)
from backend.services.market_data.market_data_service import MarketDataService
from backend.data_providers.base_market_data_provider import BaseMarketDataProvider


def candles(closes: list[float]) -> pd.DataFrame:
    index = pd.date_range("2026-08-01", periods=len(closes), freq="D")
    return pd.DataFrame(
        {
            "Open": closes,
            "High": [value + 1 for value in closes],
            "Low": [value - 1 for value in closes],
            "Close": closes,
            "Volume": [1000] * len(closes),
        },
        index=index,
    )


class CountingProvider(BaseMarketDataProvider):
    def __init__(self) -> None:
        self.calls = 0

    def download_stock_data(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> pd.DataFrame:
        self.calls += 1
        return candles([100, 101])

    def download_stock_data_batch(
        self, symbols: list[str], *, period: str = "1y", interval: str = "1d"
    ) -> dict[str, pd.DataFrame]:
        self.calls += 1
        return {symbol: candles([100, 101]) for symbol in symbols}


def test_incremental_merge_reports_insert_update_and_unchanged(tmp_path: Path) -> None:
    store = PersistentMarketDataStore(tmp_path / "scanner.sqlite3")
    first = store.merge("NSE:TCS", "NSE", "1d", candles([100, 101]), provider="test")
    corrected = candles([100, 102, 103])
    second = store.merge(
        "NSE:TCS", "NSE", "1d", corrected, provider="test"
    )

    assert (first.inserted, first.updated, first.unchanged, first.rejected) == (
        2, 0, 0, 0
    )
    assert (second.inserted, second.updated, second.unchanged, second.rejected) == (
        1, 1, 1, 0
    )
    assert store.merge_totals() == type(first)(3, 1, 1, 0)
    assert store.load("NSE:TCS", "1d")["Close"].tolist() == [100, 102, 103]


def test_malformed_rows_are_rejected_without_corrupting_history(tmp_path: Path) -> None:
    store = PersistentMarketDataStore(tmp_path / "scanner.sqlite3")
    data = candles([100, 101])
    data.loc[data.index[1], "High"] = 90

    result = store.merge("NSE:TCS", "NSE", "1d", data, provider="test")

    assert result.inserted == 1
    assert result.rejected == 1
    assert len(store.load("NSE:TCS", "1d")) == 1


def test_zero_range_is_persisted_as_a_data_break(tmp_path: Path) -> None:
    store = PersistentMarketDataStore(tmp_path / "scanner.sqlite3")
    data = candles([100])
    data.loc[data.index[0], ["Open", "High", "Low", "Close"]] = 100

    result = store.merge("NSE:TCS", "NSE", "1d", data, provider="test")

    assert result.inserted == 1
    assert result.rejected == 0
    assert len(store.load("NSE:TCS", "1d")) == 1


def test_market_data_revision_changes_only_when_candles_change(tmp_path: Path) -> None:
    store = PersistentMarketDataStore(tmp_path / "scanner.sqlite3")
    original = candles([100, 101])
    store.merge("NSE:TCS", "NSE", "1d", original, provider="test")
    first = store.revision("NSE:TCS", "1d")
    store.merge("NSE:TCS", "NSE", "1d", original, provider="test")
    unchanged = store.revision("NSE:TCS", "1d")
    store.merge("NSE:TCS", "NSE", "1d", candles([100, 102]), provider="test")
    corrected = store.revision("NSE:TCS", "1d")

    assert first == unchanged
    assert corrected != first


def test_daily_source_bootstrap_checkpoint_is_versioned_and_durable(
    tmp_path: Path,
) -> None:
    path = tmp_path / "scanner.sqlite3"
    store = PersistentMarketDataStore(path)
    store.merge("NSE:TCS", "NSE", "1d", candles([100, 101]), provider="test")
    store.mark_bootstrap(
        "NSE:TCS", "1d", "adjusted-v1", "10y", status="COMPLETE"
    )

    reopened = PersistentMarketDataStore(path)
    assert reopened.bootstrap_complete(
        "NSE:TCS", "1d", "adjusted-v1", "10y"
    )
    assert not reopened.bootstrap_complete(
        "NSE:TCS", "1d", "adjusted-v2", "10y"
    )
    assert reopened.bootstrap_progress("adjusted-v1", "10y") == {"COMPLETE": 1}


def test_completed_daily_bootstrap_is_not_downloaded_again(tmp_path: Path) -> None:
    store = PersistentMarketDataStore(tmp_path / "scanner.sqlite3")
    provider = CountingProvider()
    service = MarketDataService(provider=provider, persistent_store=store)

    service.bootstrap_daily_history_batch(
        ["TCS"], period="10y", semantics_version="adjusted-v1"
    )
    service.bootstrap_daily_history_batch(
        ["TCS"], period="10y", semantics_version="adjusted-v1"
    )

    assert provider.calls == 1
