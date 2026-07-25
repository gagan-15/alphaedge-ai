"""Historical market data API tests."""

import pandas as pd
from fastapi.testclient import TestClient

from backend.api.app import app
from backend.api import market


class StubMarketDataService:
    """Return deterministic candles without network access."""

    def get_stock_data(self, symbol: str, period: str, interval: str):
        assert symbol == "RELIANCE"
        assert period == "1y"
        assert interval == "1d"
        return pd.DataFrame(
            {
                "Open": [100.0],
                "High": [110.0],
                "Low": [95.0],
                "Close": [108.0],
                "Volume": [1200.0],
            },
            index=pd.to_datetime(["2026-07-24"]),
        )


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
