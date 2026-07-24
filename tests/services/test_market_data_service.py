"""
Tests for the market data service provider boundary.
"""

import pandas as pd
import pytest

from backend.data_providers.base_market_data_provider import BaseMarketDataProvider
from backend.services.market_data.market_data_service import MarketDataService


class StubMarketDataProvider(BaseMarketDataProvider):
    """
    Return deterministic market data without network access.
    """

    def __init__(
        self,
        data: pd.DataFrame,
    ) -> None:
        self.data = data
        self.calls: list[tuple[str, str, str]] = []

    def download_stock_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        self.calls.append(
            (
                symbol,
                period,
                interval,
            )
        )

        return self.data


def build_market_data() -> pd.DataFrame:
    """
    Build valid deterministic OHLCV data.
    """

    return pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1000, 1200],
        },
        index=pd.date_range(
            "2026-01-01",
            periods=2,
            freq="D",
        ),
    )


def test_service_uses_injected_provider() -> None:
    """
    The service forwards symbol, period, and interval to its provider.
    """

    provider = StubMarketDataProvider(
        build_market_data(),
    )
    service = MarketDataService(
        provider=provider,
    )

    result = service.get_stock_data(
        symbol="INFY.NS",
        period="6mo",
        interval="1d",
    )

    assert result.equals(provider.data)
    assert provider.calls == [
        (
            "INFY.NS",
            "6mo",
            "1d",
        )
    ]


def test_service_validates_provider_data() -> None:
    """
    Invalid provider output is rejected before reaching analysis engines.
    """

    provider = StubMarketDataProvider(
        pd.DataFrame(),
    )
    service = MarketDataService(
        provider=provider,
    )

    with pytest.raises(
        ValueError,
        match="Market data is empty",
    ):
        service.get_stock_data(
            symbol="INFY.NS",
        )
