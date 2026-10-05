"""Cached Dhan current-price overlay for persisted Dashboard results."""

from __future__ import annotations

from threading import RLock
from time import monotonic

from backend.data_providers.dhan import DhanInstrument, DhanLiveQuote, DhanMarketDataProvider


class DhanQuoteService:
    """Read-only quote cache; quote failures leave persisted results usable."""

    def __init__(self, provider: DhanMarketDataProvider | None = None, ttl_seconds: float = 5.0) -> None:
        self._provider = provider
        self._ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[float, DhanLiveQuote]] = {}
        self._lock = RLock()

    def quotes_for(self, instruments: list[DhanInstrument]) -> dict[str, DhanLiveQuote]:
        now = monotonic()
        with self._lock:
            cached = {
                item.instrument_id: entry[1]
                for item in instruments
                if (entry := self._cache.get(item.instrument_id)) is not None
                and now - entry[0] <= self._ttl_seconds
            }
        missing = [item for item in instruments if item.instrument_id not in cached]
        if not missing:
            return cached
        try:
            if self._provider is None:
                self._provider = DhanMarketDataProvider()
            provider = self._provider
            live = provider.latest_quotes(missing)
        except Exception:
            # A quote is optional.  The caller labels the exact persisted-Dhan
            # close instead of making a READY snapshot unavailable.
            return cached
        with self._lock:
            observed = monotonic()
            self._cache.update({identity: (observed, quote) for identity, quote in live.items()})
        return {**cached, **live}
