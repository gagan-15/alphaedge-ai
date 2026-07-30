from pandas import DataFrame
from threading import RLock
from time import monotonic

from backend.core.logger import logger
from backend.data_providers.base_market_data_provider import BaseMarketDataProvider
from backend.data_providers.yahoo.yahoo_provider import YahooProvider
from backend.validators.market_data_validator import MarketDataValidator


class MarketDataService:
    """
    Service responsible for fetching market data.
    """

    def __init__(
        self,
        provider: BaseMarketDataProvider | None = None,
    ) -> None:
        """
        Initialize the service with a market data provider.

        Args:
            provider:
                Optional provider implementation. Yahoo Finance is used
                by default during development.
        """

        self._provider = provider or YahooProvider()

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

    _cache: dict[tuple[str, str, str], tuple[float, DataFrame]] = {}
    _cache_lock = RLock()
    _cache_ttl_seconds = 300.0
