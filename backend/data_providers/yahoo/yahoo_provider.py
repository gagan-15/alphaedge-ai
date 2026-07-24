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

        data = yf.download(
            tickers=symbol,
            period=period,
            interval=interval,
            progress=False,
        )

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            data = data[["Open", "High", "Low", "Close", "Volume"]]

        data.columns.name = None
        data = data.dropna()
        data = data.sort_index()

        return data
