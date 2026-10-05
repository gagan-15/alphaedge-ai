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

    def download_stock_data_since(
        self,
        symbol: str,
        *,
        start: object,
        interval: str = "1d",
    ) -> DataFrame:
        """Download an incremental window when the provider supports it.

        Providers without a native date-range API retain backward compatibility
        by returning their normal history. The persistence layer still performs
        a deterministic timestamp merge.
        """

        del start
        return self.download_stock_data(symbol, period="1y", interval=interval)

    def download_stock_data_batch(
        self,
        symbols: list[str],
        *,
        period: str = "1y",
        interval: str = "1d",
    ) -> dict[str, DataFrame]:
        """Download a bounded batch; providers may override efficiently."""

        return {
            symbol: self.download_stock_data(symbol, period=period, interval=interval)
            for symbol in symbols
        }
