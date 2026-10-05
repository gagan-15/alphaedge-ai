"""Dhan-only Dashboard benchmark quote service."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import monotonic

from backend.data_providers.dhan import DhanMarketDataProvider, DhanMarketQuote


@dataclass(frozen=True)
class DhanIndexIdentity:
    """Official Dhan index-market identity, verified against its master."""

    name: str
    exchange: str
    exchange_segment: str
    security_id: str
    instrument: str = "INDEX"


@dataclass(frozen=True)
class DhanIndexQuote:
    identity: DhanIndexIdentity
    price: float
    change_percent: float | None
    as_of: str


# Dhan's master identifies all four as INDEX records. Its Market Quote
# Annexure requires IDX_I for index values, including the BSE SENSEX record.
DHAN_DASHBOARD_INDEXES: dict[str, DhanIndexIdentity] = {
    "nifty50": DhanIndexIdentity("NIFTY 50", "NSE", "IDX_I", "13"),
    "sensex": DhanIndexIdentity("SENSEX", "BSE", "IDX_I", "51"),
    "bank_nifty": DhanIndexIdentity("BANK NIFTY", "NSE", "IDX_I", "25"),
    "india_vix": DhanIndexIdentity("INDIA VIX", "NSE", "IDX_I", "21"),
}


class DhanIndexQuoteService:
    """Small cached read path for the four Dashboard index cards only."""

    def __init__(
        self,
        provider: DhanMarketDataProvider | None = None,
        ttl_seconds: float = 5.0,
    ) -> None:
        self._provider = provider
        self._ttl_seconds = ttl_seconds
        self._cache: tuple[float, dict[str, DhanIndexQuote]] | None = None
        self._lock = RLock()

    def quotes(self) -> dict[str, DhanIndexQuote]:
        now = monotonic()
        with self._lock:
            if self._cache and now - self._cache[0] <= self._ttl_seconds:
                return self._cache[1]
        try:
            if self._provider is None:
                self._provider = DhanMarketDataProvider()
            raw = self._provider.latest_market_quotes(
                {
                    key: (identity.exchange_segment, identity.security_id)
                    for key, identity in DHAN_DASHBOARD_INDEXES.items()
                }
            )
        except Exception:
            # Unavailable is explicit at the response layer; no zero movement
            # is ever manufactured for a missing quote.
            return {}
        quotes = {
            key: self._to_index_quote(DHAN_DASHBOARD_INDEXES[key], quote)
            for key, quote in raw.items()
            if key in DHAN_DASHBOARD_INDEXES
        }
        with self._lock:
            self._cache = (now, quotes)
        return quotes

    @staticmethod
    def _to_index_quote(
        identity: DhanIndexIdentity, quote: DhanMarketQuote
    ) -> DhanIndexQuote:
        previous = quote.previous_close
        change_percent = (
            quote.net_change / previous * 100
            if previous is not None and previous > 0
            else None
        )
        return DhanIndexQuote(
            identity=identity,
            price=quote.price,
            change_percent=change_percent,
            as_of=quote.as_of,
        )
