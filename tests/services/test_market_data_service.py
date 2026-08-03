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


def test_service_returns_valid_provider_data_unchanged() -> None:
    """Canonical validation preserves existing valid service behaviour."""

    data = build_market_data()
    provider = StubMarketDataProvider(data)
    service = MarketDataService(provider=provider)

    result = service.get_stock_data(
        symbol="VALIDATION-REGRESSION.NS",
    )

    pd.testing.assert_frame_equal(result, data)


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("High", 98.0, "High is below Low"),
        ("Open", 104.0, "Open is outside High-Low range"),
        ("Close", 98.0, "Close is outside High-Low range"),
    ],
)
def test_service_rejects_malformed_provider_ohlc(
    column: str,
    value: float,
    message: str,
) -> None:
    """Malformed provider candles never reach analysis consumers."""

    data = build_market_data()
    data.loc[data.index[0], column] = value
    provider = StubMarketDataProvider(data)
    service = MarketDataService(provider=provider)

    with pytest.raises(ValueError, match=message):
        service.get_stock_data(
            symbol=f"MALFORMED-{column}.NS",
        )


def test_service_rejects_zero_range_provider_candle() -> None:
    """A zero-range provider candle is rejected at the service boundary."""

    data = build_market_data()
    data.loc[data.index[0], ["Open", "High", "Low", "Close"]] = [
        100.0,
        100.0,
        100.0,
        100.0,
    ]
    provider = StubMarketDataProvider(data)
    service = MarketDataService(provider=provider)

    with pytest.raises(ValueError, match="zero-range candle"):
        service.get_stock_data(
            symbol="ZERO-RANGE.NS",
        )
