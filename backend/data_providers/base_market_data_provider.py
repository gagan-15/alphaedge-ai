"""
Market data provider contract.

All external market data integrations implement this contract so application
services remain independent from a specific vendor.
"""

from abc import ABC, abstractmethod

from pandas import DataFrame


class BaseMarketDataProvider(ABC):
    """
    Define the interface for historical market data providers.
    """

    @abstractmethod
    def download_stock_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> DataFrame:
        """
        Download normalized OHLCV data for a symbol.

        Args:
            symbol:
                Provider-compatible instrument symbol.
            period:
                Historical lookback period.
            interval:
                Candle interval.

        Returns:
            A date-sorted DataFrame containing Open, High, Low, Close,
            and Volume columns.
        """

        raise NotImplementedError
