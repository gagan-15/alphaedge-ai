"""Historical market data API tests."""

import pandas as pd
from fastapi.testclient import TestClient

from backend.api.app import app
from backend.api import market
from backend.validators.market_data_validator import ValidatedMarketDataSegments


class StubMarketDataService:
    """Return deterministic candles without network access."""

    def get_stock_data_segments(self, symbol: str, period: str, interval: str):
        assert symbol == "RELIANCE"
        assert period == "1y"
        assert interval == "1d"
        data = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [110.0],
                "Low": [95.0],
                "Close": [108.0],
                "Volume": [1200.0],
            },
            index=pd.to_datetime(["2026-07-24"]),
        )
        return ValidatedMarketDataSegments((data,), ())


def test_get_candles(monkeypatch) -> None:
    monkeypatch.setattr(
        market,
        "_market_data_service",
        StubMarketDataService(),
    )
    response = TestClient(app).get(
        "/market/candles?symbol=RELIANCE&period=1y&interval=1d",
    )

    assert response.status_code == 200
    result = response.json()
    assert result["symbol"] == "RELIANCE"
    assert result["delayed"] is True
    assert result["candles"][0]["close"] == 108.0


def test_rejects_invalid_market_symbol() -> None:
    response = TestClient(app).get(
        "/market/candles?symbol=../../secret",
    )

    assert response.status_code == 400


def test_accepts_nse_symbol_with_ampersand(monkeypatch) -> None:
    service = StubMarketDataService()
    monkeypatch.setattr(market, "_market_data_service", service)

    original = service.get_stock_data_segments

    def get_segments(symbol: str, period: str, interval: str):
        assert symbol == "M&MFIN"
        return original("RELIANCE", period, interval)

    service.get_stock_data_segments = get_segments
    response = TestClient(app).get(
        "/market/candles?symbol=M%26MFIN&period=1y&interval=1d",
    )

    assert response.status_code == 200
    assert response.json()["symbol"] == "M&MFIN"


def test_get_candles_uses_requested_chart_timeframe(monkeypatch) -> None:
    """A monthly zone chart must receive monthly candles, not daily candles."""

    class MonthlyMarketDataService:
        def get_stock_data_segments(
            self, symbol: str, period: str, interval: str
        ):
            assert period == "10y"
            assert interval == "1d"
            index = pd.date_range("2026-01-01", periods=60, freq="D")
            data = pd.DataFrame(
                {
                    "Open": range(100, 160),
                    "High": range(101, 161),
                    "Low": range(99, 159),
                    "Close": range(100, 160),
                    "Volume": [1000] * 60,
                },
                index=index,
            )
            return ValidatedMarketDataSegments((data,), ())

    monkeypatch.setattr(
        market,
        "_market_data_service",
        MonthlyMarketDataService(),
    )
    response = TestClient(app).get(
        "/market/candles?symbol=RELIANCE&period=10y"
        "&interval=1d&timeframe=1M",
    )

    assert response.status_code == 200
    result = response.json()
    assert result["interval"] == "1M"
    assert len(result["candles"]) == 3
