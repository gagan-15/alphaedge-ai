from pandas import DataFrame
from pandas import Timedelta
from threading import RLock
from time import monotonic
from pathlib import Path
import os

from backend.core.logger import logger
from backend.data_providers.base_market_data_provider import BaseMarketDataProvider
from backend.data_providers.yahoo.yahoo_provider import YahooProvider
from backend.config.market_data_providers import MARKET_DATA_PROVIDER
from backend.validators.market_data_validator import (
    MarketDataValidator,
    ValidatedMarketDataSegments,
)
from backend.services.market_data.persistent_market_data_store import (
    CandleMergeResult,
    PersistentMarketDataStore,
)


class MarketDataService:
    """
    Service responsible for fetching market data.
    """

    def __init__(
        self,
        provider: BaseMarketDataProvider | None = None,
        persistent_store: PersistentMarketDataStore | None = None,
    ) -> None:
        """
        Initialize the service with a market data provider.

        Args:
            provider:
                Optional provider implementation. Yahoo Finance is used
                by default during development.
        """

        if provider is not None:
            self._provider = provider
        elif MARKET_DATA_PROVIDER == "dhan":
            # Dhan is source-labelled and opt-in. Existing Yahoo data remain
            # untouched; callers must materialize into a Dhan-specific store.
            from backend.data_providers.dhan import DhanMarketDataProvider

            self._provider = DhanMarketDataProvider()
        else:
            self._provider = YahooProvider()
        # Test/fake providers stay isolated unless persistence is explicitly
        # injected. Production's default provider uses durable OHLCV storage.
        if persistent_store is not None:
            self._persistent_store = persistent_store
        elif provider is not None:
            self._persistent_store = None
        elif MARKET_DATA_PROVIDER == "dhan":
            dhan_path = Path(
                os.getenv(
                    "DHAN_PRODUCTION_DATABASE_PATH",
                    "backend/data/scanner/alphaedge-dhan.sqlite3",
                )
            )
            self._persistent_store = PersistentMarketDataStore(dhan_path)
        else:
            self._persistent_store = PersistentMarketDataStore()
        self._last_merge_result: dict[tuple[str, str], CandleMergeResult] = {}

    def get_stock_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> DataFrame:
        """
        Get stock market data.
        """

        logger.info(
            "Downloading market data for %s.",
            symbol,
        )
        cache_key = (symbol.strip().upper(), period, interval)
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached and monotonic() - cached[0] < self._cache_ttl_seconds:
                return cached[1].copy()

        data = self._provider.download_stock_data(
            symbol=symbol,
            period=period,
            interval=interval,
        )

        # Validate the downloaded market data.
        MarketDataValidator.validate(data)
        with self._cache_lock:
            self._cache[cache_key] = (monotonic(), data.copy())

        logger.info("Market data validation completed successfully.")

        return data

    def get_stock_data_segments(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> ValidatedMarketDataSegments:
        """Return valid segments without allowing patterns across bad candles."""

        logger.info("Downloading segmented market data for %s.", symbol)
        cache_key = (symbol.strip().upper(), period, interval)
        with self._cache_lock:
            cached = self._segment_cache.get(cache_key)
            if cached and monotonic() - cached[0] < self._cache_ttl_seconds:
                result = cached[1]
                return ValidatedMarketDataSegments(
                    segments=tuple(segment.copy() for segment in result.segments),
                    zero_range_rows=result.zero_range_rows,
                )

        data: DataFrame
        store = self._persistent_store
        instrument_id = f"NSE:{symbol.strip().upper()}"
        if store is not None:
            latest = store.latest_timestamp(instrument_id, interval)
            if latest is None:
                downloaded = self._provider.download_stock_data(
                    symbol=symbol,
                    period=period,
                    interval=interval,
                )
            else:
                overlap = Timedelta(days=7 if interval == "1d" else 2)
                downloaded = self._provider.download_stock_data_since(
                    symbol,
                    start=latest - overlap,
                    interval=interval,
                )
            merge = store.merge(
                instrument_id,
                "NSE",
                interval,
                downloaded,
                provider=type(self._provider).__name__,
            )
            self._last_merge_result[(symbol.strip().upper(), interval)] = merge
            data = store.load(instrument_id, interval)
        else:
            data = self._provider.download_stock_data(
                symbol=symbol,
                period=period,
                interval=interval,
            )
        result = MarketDataValidator.validate_segments(data)
        with self._cache_lock:
            self._segment_cache[cache_key] = (monotonic(), result)

        if result.zero_range_rows:
            logger.warning(
                "Skipped %s zero-range candle(s) for %s and created "
                "%s valid segment(s).",
                result.skipped_zero_range_count,
                symbol,
                len(result.segments),
            )
        return ValidatedMarketDataSegments(
            segments=tuple(segment.copy() for segment in result.segments),
            zero_range_rows=result.zero_range_rows,
        )

    _cache: dict[tuple[str, str, str], tuple[float, DataFrame]] = {}
    _segment_cache: dict[
        tuple[str, str, str], tuple[float, ValidatedMarketDataSegments]
    ] = {}
    _cache_lock = RLock()
    _cache_ttl_seconds = 300.0

    def persisted_revision(self, symbol: str, interval: str) -> str | None:
        """Expose an operational candle revision without exposing storage details."""

        if self._persistent_store is None:
            return None
        return self._persistent_store.revision(
            f"NSE:{symbol.strip().upper()}", interval
        )

    def has_persisted_data(self, symbol: str, interval: str) -> bool:
        return bool(
            self._persistent_store
            and self._persistent_store.latest_timestamp(
                f"NSE:{symbol.strip().upper()}", interval
            ) is not None
        )

    def load_persisted_segments(
        self,
        symbol: str,
        *,
        period: str,
        interval: str,
    ) -> ValidatedMarketDataSegments:
        """Load and cache durable candles without making a provider request."""

        store = self._persistent_store
        if store is None:
            raise ValueError("Persistent market-data storage is unavailable.")
        normalized = symbol.strip().upper()
        data = store.load(f"NSE:{normalized}", interval)
        result = MarketDataValidator.validate_segments(data)
        cache_key = (normalized, period, interval)
        with self._cache_lock:
            self._segment_cache[cache_key] = (monotonic(), result)
        return ValidatedMarketDataSegments(
            segments=tuple(segment.copy() for segment in result.segments),
            zero_range_rows=result.zero_range_rows,
        )

    def prefetch_stock_data_batch(
        self,
        symbols: list[str],
        *,
        period: str,
        interval: str,
    ) -> dict[str, CandleMergeResult]:
        """Fetch and persist a bounded batch without retaining full histories."""

        store = self._persistent_store
        if store is None or not symbols:
            return {}
        frames = self._provider.download_stock_data_batch(
            symbols, period=period, interval=interval
        )
        merged: dict[str, CandleMergeResult] = {}
        for symbol, frame in frames.items():
            normalized = symbol.strip().upper()
            result = store.merge(
                f"NSE:{normalized}", "NSE", interval, frame,
                provider=type(self._provider).__name__,
            )
            merged[normalized] = result
        return merged

    def bootstrap_daily_history_batch(
        self,
        symbols: list[str],
        *,
        period: str,
        semantics_version: str,
        final_attempt: bool = False,
    ) -> dict[str, CandleMergeResult]:
        """Persist one bounded full-history batch and checkpoint each symbol."""

        store = self._persistent_store
        if store is None or not symbols:
            return {}
        pending = [
            symbol.strip().upper()
            for symbol in symbols
            if not store.bootstrap_complete(
                f"NSE:{symbol.strip().upper()}", "1d", semantics_version, period
            )
        ]
        if not pending:
            return {}
        frames = self._provider.download_stock_data_batch(
            pending, period=period, interval="1d"
        )
        merged: dict[str, CandleMergeResult] = {}
        for symbol in pending:
            instrument_id = f"NSE:{symbol}"
            frame = frames.get(symbol)
            if frame is None or frame.empty:
                store.mark_bootstrap(
                    instrument_id, "1d", semantics_version, period,
                    status="FAILED" if final_attempt else "RETRYABLE",
                    error="Provider returned no Daily history.",
                )
                continue
            try:
                result = store.merge(
                    instrument_id, "NSE", "1d", frame,
                    provider=type(self._provider).__name__,
                )
                store.mark_bootstrap(
                    instrument_id, "1d", semantics_version, period,
                    status="COMPLETE",
                )
                merged[symbol] = result
            except Exception as error:
                store.mark_bootstrap(
                    instrument_id, "1d", semantics_version, period,
                    status="FAILED" if final_attempt else "RETRYABLE",
                    error=str(error),
                )
        return merged

    def daily_bootstrap_complete(
        self,
        symbol: str,
        *,
        period: str,
        semantics_version: str,
    ) -> bool:
        store = self._persistent_store
        return bool(
            store
            and store.bootstrap_complete(
                f"NSE:{symbol.strip().upper()}", "1d", semantics_version, period
            )
        )

    def daily_bootstrap_progress(
        self, *, period: str, semantics_version: str,
        universe: str | None = None,
    ) -> dict[str, int]:
        return (
            self._persistent_store.bootstrap_progress(
                semantics_version, period, universe
            )
            if self._persistent_store
            else {}
        )

    def persisted_universe_revision(self, interval: str) -> str | None:
        return (
            self._persistent_store.universe_revision(interval)
            if self._persistent_store
            else None
        )

    def release_symbol_cache(self, symbol: str) -> None:
        """Release transient frames after bounded background symbol work."""

        normalized = symbol.strip().upper()
        with self._cache_lock:
            for key in tuple(self._cache):
                if key[0] == normalized:
                    self._cache.pop(key, None)
            for key in tuple(self._segment_cache):
                if key[0] == normalized:
                    self._segment_cache.pop(key, None)
