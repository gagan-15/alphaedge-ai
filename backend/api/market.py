"""Read-only historical market data API."""

import re

from fastapi import APIRouter, HTTPException, Query

from backend.api.models.market_response import (
    CandleResponse,
    CandleSeriesResponse,
)
from backend.services.market_data.market_data_service import MarketDataService

market_router = APIRouter(prefix="/market", tags=["Market Data"])

_market_data_service = MarketDataService()
_symbol_pattern = re.compile(r"^[A-Z0-9.^_-]{1,24}$")
_allowed_periods = {"1mo", "3mo", "6mo", "1y", "2y", "5y"}
_allowed_intervals = {"1d", "1h", "30m", "15m"}


@market_router.get("/candles", response_model=CandleSeriesResponse)
def get_candles(
    symbol: str = Query("RELIANCE"),
    period: str = Query("1y"),
    interval: str = Query("1d"),
) -> CandleSeriesResponse:
    """Return delayed historical candles for research charting."""

    normalized_symbol = symbol.strip().upper()
    if not _symbol_pattern.fullmatch(normalized_symbol):
        raise HTTPException(status_code=400, detail="Invalid market symbol.")
    if period not in _allowed_periods:
        raise HTTPException(status_code=400, detail="Unsupported period.")
    if interval not in _allowed_intervals:
        raise HTTPException(status_code=400, detail="Unsupported interval.")

    try:
        data = _market_data_service.get_stock_data(
            symbol=normalized_symbol,
            period=period,
            interval=interval,
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Historical market data is temporarily unavailable.",
        ) from error

    candles = tuple(
        CandleResponse(
            time=index.to_pydatetime(),
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=float(row["Volume"]),
        )
        for index, row in data.iterrows()
    )

    return CandleSeriesResponse(
        symbol=normalized_symbol,
        period=period,
        interval=interval,
        source="Yahoo Finance development feed",
        delayed=True,
        candles=candles,
    )
