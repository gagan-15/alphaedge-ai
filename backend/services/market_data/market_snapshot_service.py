"""Cached delayed benchmark and universe-breadth snapshots."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from time import monotonic

from backend.services.market_data.market_data_service import MarketDataService
from backend.services.scanner.universe_service import UniverseName, UniverseService


@dataclass(frozen=True)
class QuoteSnapshot:
    symbol: str
    price: float
    change_percent: float


@dataclass(frozen=True)
class MarketSnapshot:
    quotes: dict[str, QuoteSnapshot]
    advancing: int
    declining: int
    unchanged: int
    total_symbols: int
    processed_symbols: int
    source: str
    data_status: str
    updated_at: datetime


class MarketSnapshotService:
    """Provide one reusable cached source for dashboard and ticker data."""

    _benchmark_symbols = {
        "nifty50": "^NSEI",
        "sensex": "^BSESN",
        "bank_nifty": "^NSEBANK",
        "india_vix": "^INDIAVIX",
    }
    _cache: dict[str, tuple[float, MarketSnapshot]] = {}
    _refreshing: set[str] = set()
    _lock = RLock()
    _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="market-snapshot")
    _ttl_seconds = 300.0

    def __init__(
        self,
        market_data: MarketDataService | None = None,
        universe_service: UniverseService | None = None,
    ) -> None:
        self._market_data = market_data or MarketDataService()
        self._universe_service = universe_service or UniverseService()

    def get_snapshot(
        self,
        universe: UniverseName = "nse500",
        supplied_symbols: list[str] | None = None,
    ) -> MarketSnapshot:
        key = self._cache_key(universe, supplied_symbols)
        with self._lock:
            cached = self._cache.get(key)
            fresh = cached and monotonic() - cached[0] < self._ttl_seconds
        if fresh:
            return cached[1]

        # Benchmarks are a small request and must never be replaced by demo values.
        benchmark_quotes = self._load_quotes(self._benchmark_symbols)
        symbols = self._universe_service.get_symbols(universe, supplied_symbols)
        with self._lock:
            previous = self._cache.get(key)
            if key not in self._refreshing:
                self._refreshing.add(key)
                self._executor.submit(
                    self._refresh_breadth,
                    key,
                    universe,
                    supplied_symbols,
                    benchmark_quotes,
                )
        if previous:
            old = previous[1]
            return MarketSnapshot(
                quotes=benchmark_quotes or old.quotes,
                advancing=old.advancing,
                declining=old.declining,
                unchanged=old.unchanged,
                total_symbols=len(symbols),
                processed_symbols=old.processed_symbols,
                source="Yahoo Finance development feed",
                data_status="cached",
                updated_at=old.updated_at,
            )
        return MarketSnapshot(
            quotes=benchmark_quotes,
            advancing=0,
            declining=0,
            unchanged=0,
            total_symbols=len(symbols),
            processed_symbols=0,
            source="Yahoo Finance development feed",
            data_status="refreshing",
            updated_at=datetime.now(UTC),
        )

    def _refresh_breadth(
        self,
        key: str,
        universe: UniverseName,
        supplied_symbols: list[str] | None,
        benchmark_quotes: dict[str, QuoteSnapshot],
    ) -> None:
        advancing = declining = unchanged = processed = 0
        symbols = self._universe_service.get_symbols(universe, supplied_symbols)

        def direction(symbol: str) -> int | None:
            try:
                data = self._market_data.get_stock_data(
                    symbol,
                    period="1mo",
                    interval="1d",
                )
                if len(data) < 2:
                    return None
                difference = float(data["Close"].iloc[-1] - data["Close"].iloc[-2])
                return 1 if difference > 0 else -1 if difference < 0 else 0
            except Exception:
                return None

        with ThreadPoolExecutor(
            max_workers=6,
            thread_name_prefix="market-breadth",
        ) as pool:
            for result in pool.map(direction, symbols):
                if result is None:
                    continue
                processed += 1
                advancing += result > 0
                declining += result < 0
                unchanged += result == 0
        snapshot = MarketSnapshot(
            quotes=benchmark_quotes or self._load_quotes(self._benchmark_symbols),
            advancing=advancing,
            declining=declining,
            unchanged=unchanged,
            total_symbols=len(symbols),
            processed_symbols=processed,
            source="Yahoo Finance development feed",
            data_status="delayed",
            updated_at=datetime.now(UTC),
        )
        with self._lock:
            self._cache[key] = (monotonic(), snapshot)
            self._refreshing.discard(key)

    def _load_quotes(self, symbols: dict[str, str]) -> dict[str, QuoteSnapshot]:
        def load(item: tuple[str, str]) -> tuple[str, QuoteSnapshot] | None:
            name, symbol = item
            try:
                data = self._market_data.get_stock_data(
                    symbol,
                    period="1mo",
                    interval="1d",
                )
                latest = float(data["Close"].iloc[-1])
                previous = float(data["Close"].iloc[-2])
                change = (latest - previous) / previous * 100
                return name, QuoteSnapshot(
                    symbol=name,
                    price=latest,
                    change_percent=change,
                )
            except Exception:
                return None

        with ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix="market-benchmark",
        ) as pool:
            return dict(
                result for result in pool.map(load, symbols.items()) if result
            )

    @staticmethod
    def _cache_key(universe: str, supplied_symbols: list[str] | None) -> str:
        return f"{universe}:{','.join(sorted(supplied_symbols or []))}"
