"""
Yahoo Finance Data Provider

Purpose:
    Download historical stock market data from Yahoo Finance.

Author:
    AlphaEdge AI
"""

import pandas as pd
import yfinance as yf

from backend.data_providers.base_market_data_provider import BaseMarketDataProvider
from backend.services.market_data.canonical_source_semantics import (
    YAHOO_AUTO_ADJUST,
)


class YahooProvider(BaseMarketDataProvider):
    """
    Yahoo Finance Provider
    """

    def download_stock_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Download and clean historical stock data.
        """

        provider_symbol = self._normalize_symbol(
            symbol,
        )

        data = yf.download(
            tickers=provider_symbol,
            period=period,
            interval=interval,
            auto_adjust=YAHOO_AUTO_ADJUST,
            progress=False,
        )

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            data = data[["Open", "High", "Low", "Close", "Volume"]]

        data.columns.name = None
        data = data.dropna()
        data = data.sort_index()

        return data

    def download_stock_data_since(
        self,
        symbol: str,
        *,
        start: object,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Use Yahoo's date-range request for correction-overlap updates."""

        data = yf.download(
            tickers=self._normalize_symbol(symbol),
            start=start,
            interval=interval,
            auto_adjust=YAHOO_AUTO_ADJUST,
            progress=False,
        )
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        data = data[["Open", "High", "Low", "Close", "Volume"]]
        data.columns.name = None
        return data.dropna().sort_index()

    def download_stock_data_batch(
        self,
        symbols: list[str],
        *,
        period: str = "1y",
        interval: str = "1d",
    ) -> dict[str, pd.DataFrame]:
        """Use Yahoo's multi-ticker request while preserving per-symbol frames."""

        if not symbols:
            return {}
        normalized = {symbol: self._normalize_symbol(symbol) for symbol in symbols}
        data = yf.download(
            tickers=list(normalized.values()), period=period, interval=interval,
            group_by="ticker", threads=True, progress=False,
            auto_adjust=YAHOO_AUTO_ADJUST,
        )
        output: dict[str, pd.DataFrame] = {}
        for symbol, provider_symbol in normalized.items():
            try:
                frame = (
                    data[provider_symbol]
                    if isinstance(data.columns, pd.MultiIndex)
                    else data
                )
                frame = frame[["Open", "High", "Low", "Close", "Volume"]]
                frame.columns.name = None
                frame = frame.dropna().sort_index()
                if not frame.empty:
                    output[symbol] = frame
            except (KeyError, TypeError):
                continue
        return output

    @staticmethod
    def _normalize_symbol(
        symbol: str,
    ) -> str:
        """
        Add the NSE suffix to plain equity symbols.
        """

        normalized = symbol.strip().upper()

        if "." not in normalized and not normalized.startswith("^"):
            return f"{normalized}.NS"

        return normalized
