"""Read-only historical market data API."""

import re
from datetime import date

from fastapi import APIRouter, HTTPException, Query
from pandas import concat
from pandas import DateOffset
import pandas as pd

from backend.api.models.market_response import (
    CandleResponse,
    CandleSeriesResponse,
)
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.market_data.dhan_shadow_store import DhanShadowStore
from backend.config.market_data_providers import MARKET_DATA_PROVIDER
from backend.services.market_data.timeframe_service import (
    INTRADAY_SOURCES,
    TIMEFRAME_RULES,
    aggregate_timeframe,
)
from backend.services.scanner.universe_service import UniverseService

market_router = APIRouter(prefix="/market", tags=["Market Data"])

_market_data_service = MarketDataService()
_dhan_shadow_store = DhanShadowStore()
_default_symbol = UniverseService().get_symbols("nse500")[0]
_symbol_pattern = re.compile(r"^[A-Z0-9.&^_-]{1,24}$")
_allowed_periods = {"1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"}
_allowed_intervals = {"1d", "1h", "30m", "15m", "5m"}


@market_router.get("/candles", response_model=CandleSeriesResponse)
def get_candles(
    symbol: str = Query(_default_symbol),
    period: str = Query("1y"),
    interval: str = Query("1d"),
    timeframe: str = Query("1D"),
    instrument_id: str | None = Query(default=None, max_length=64),
    formation_date: str | None = Query(default=None, max_length=10),
) -> CandleSeriesResponse:
    """Return delayed historical candles for research charting."""

    normalized_symbol = symbol.strip().upper()
    if not _symbol_pattern.fullmatch(normalized_symbol):
        raise HTTPException(status_code=400, detail="Invalid market symbol.")
    if period not in _allowed_periods:
        raise HTTPException(status_code=400, detail="Unsupported period.")
    if interval not in _allowed_intervals:
        raise HTTPException(status_code=400, detail="Unsupported interval.")
    if timeframe not in TIMEFRAME_RULES:
        raise HTTPException(status_code=400, detail="Unsupported timeframe.")
    if timeframe not in INTRADAY_SOURCES and timeframe != "1D" and interval != "1d":
        raise HTTPException(
            status_code=400,
            detail="Aggregated timeframes require daily source candles.",
        )
    parsed_formation_date: date | None = None
    if formation_date is not None:
        try:
            parsed_formation_date = date.fromisoformat(formation_date)
        except ValueError as error:
            raise HTTPException(status_code=400, detail="Invalid formation date.") from error

    try:
        if MARKET_DATA_PROVIDER == "dhan":
            # Dashboard Dhan zones are charted only from persisted Dhan
            # candles. This includes the bounded intraday pilot and never
            # falls back to Yahoo or calls a provider API while a chart opens.
            instrument = (
                _dhan_shadow_store.active_instrument_by_id(instrument_id)
                if instrument_id else _dhan_shadow_store.active_instrument_for_symbol(normalized_symbol)
            )
            if instrument is None:
                raise LookupError("Dhan instrument identity is unavailable.")
            if str(instrument["symbol"]).upper() != normalized_symbol:
                raise LookupError("Dhan instrument identity does not match the symbol.")
            source_timeframe = timeframe if timeframe in INTRADAY_SOURCES else "1D"
            data = _dhan_shadow_store.load(
                str(instrument["instrument_id"]), source_timeframe
            )
            if data.empty:
                raise LookupError("Persisted Dhan candles are unavailable.")
            period_days = {
                "1mo": 31, "3mo": 93, "6mo": 186, "1y": 366,
                "2y": 732, "5y": 1830, "10y": 3660,
            }
            cutoff = data.index[-1] - DateOffset(days=period_days[period])
            if parsed_formation_date is not None:
                # Preserve the actual formation candle and a small lead-in. The
                # zone's full-series base index is never used against a clipped
                # chart window.
                formation_timestamp = pd.Timestamp(parsed_formation_date)
                if data.index.tz is not None:
                    formation_timestamp = formation_timestamp.tz_localize(
                        data.index.tz
                    )
                formation_position = data.index.get_indexer(
                    [formation_timestamp], method="nearest"
                )[0]
                if formation_position < 0:
                    raise LookupError("Formation candle is unavailable.")
                formation_cutoff = data.index[formation_position] - DateOffset(days=21)
                cutoff = min(cutoff, formation_cutoff)
            data = data[data.index >= cutoff]
            if timeframe not in INTRADAY_SOURCES:
                data = aggregate_timeframe(data, timeframe)
            source = "Dhan persisted delayed OHLCV"
        else:
            source = "Yahoo Finance development feed"
            if timeframe in INTRADAY_SOURCES:
                period, interval = INTRADAY_SOURCES[timeframe]
            validated = _market_data_service.get_stock_data_segments(
                symbol=normalized_symbol,
                period=period,
                interval=interval,
            )
            # Charting may display valid candles on both sides of a data break.
            # Invalid rows remain excluded; no values are interpolated or created.
            data = concat(validated.segments).sort_index()
            data = aggregate_timeframe(data, timeframe)
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
        interval=timeframe,
        source=source,
        delayed=True,
        candles=candles,
    )
