"""Aggregate daily OHLCV candles into research timeframes."""

from pandas import DataFrame

TIMEFRAME_RULES: dict[str, str | None] = {
    "1D": None,
    "1W": "W-FRI",
    "1M": "ME",
    "3M": "QE",
    "6M": "2QE",
    "1Y": "YE",
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
    return data.resample(rule).agg(aggregations).dropna(subset=["Close"])
