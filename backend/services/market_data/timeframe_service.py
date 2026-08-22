"""Aggregate daily OHLCV candles into research timeframes."""

from pandas import DataFrame

TIMEFRAME_RULES: dict[str, str | None] = {
    "5m": None,
    "15m": None,
    "75m": "75min",
    "125m": "125min",
    "1H": None,
    "2H": "2h",
    "4H": "4h",
    "6H": "6h",
    "1D": None,
    "1W": "W-FRI",
    "1M": "ME",
    "3M": "QE",
    "6M": "2QE",
    "1Y": "YE",
}

INTRADAY_SOURCES: dict[str, tuple[str, str]] = {
    "5m": ("1mo", "5m"),
    "15m": ("1mo", "15m"),
    "75m": ("1mo", "15m"),
    "125m": ("1mo", "5m"),
    "1H": ("1mo", "1h"),
    "2H": ("1mo", "1h"),
    "4H": ("1mo", "1h"),
    "6H": ("1mo", "1h"),
}


def aggregate_timeframe(data: DataFrame, timeframe: str) -> DataFrame:
    """Return candles at the requested timeframe."""

    rule = TIMEFRAME_RULES[timeframe]
    if rule is None:
        return data
    aggregations = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
    }
    if "Volume" in data.columns:
        aggregations["Volume"] = "sum"
    intraday = timeframe in {"75m", "125m", "2H", "4H", "6H"}
    resampler = (
        data.resample(rule, origin="start_day", offset="9h15min")
        if intraday
        else data.resample(rule)
    )
    return resampler.agg(aggregations).dropna(subset=["Close"])
