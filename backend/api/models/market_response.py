"""Market data API response models."""

from datetime import datetime

from pydantic import BaseModel


class CandleResponse(BaseModel):
    """One normalized OHLCV candle."""

    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class CandleSeriesResponse(BaseModel):
    """Historical candles and reader-facing source information."""

    symbol: str
    period: str
    interval: str
    source: str
    delayed: bool
    candles: tuple[CandleResponse, ...]
