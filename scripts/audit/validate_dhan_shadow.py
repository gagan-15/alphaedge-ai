"""Bounded, credential-safe Dhan shadow migration evidence report."""

from __future__ import annotations

import json
from datetime import date, timedelta
from time import perf_counter

import pandas as pd
from dotenv import load_dotenv

from backend.data_providers.dhan import DhanMarketDataProvider
from backend.data_providers.yahoo.yahoo_provider import YahooProvider
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.services.market_data.dhan_shadow_store import DhanShadowStore
from backend.validators.market_data_validator import MarketDataValidator


def normalized(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.index = pd.Index(pd.to_datetime(result.index).date)
    return result[~result.index.duplicated(keep="last")]


def zone_keys(frame: pd.DataFrame) -> set[tuple[object, ...]]:
    output: set[tuple[object, ...]] = set()
    for segment in MarketDataValidator.validate_segments(frame).segments:
        for zone in ZoneDetectionEngine().detect_zones(segment):
            output.add(
                (
                    zone.zone_type.value,
                    zone.pattern_type,
                    round(zone.lower_price, 4),
                    round(zone.upper_price, 4),
                )
            )
    return output


def compare(symbol: str, dhan: DhanMarketDataProvider) -> dict[str, object]:
    end = date.today()
    dhan_frame = dhan.download_instrument_data(
        dhan.resolve(symbol),
        start=end - timedelta(days=366 * 5),
        end=end,
        interval="1d",
    )
    yahoo_frame = YahooProvider().download_stock_data(symbol, period="5y")
    left, right = normalized(yahoo_frame), normalized(dhan_frame)
    dates = left.index.intersection(right.index)
    if dates.empty:
        return {"symbol": symbol, "error": "NO_COMMON_DATES"}
    left, right = left.loc[dates], right.loc[dates]
    absolute = (
        left[["Open", "High", "Low", "Close"]] - right[["Open", "High", "Low", "Close"]]
    ).abs()
    identical = (absolute <= 1e-8).all(axis=1)
    yahoo_zones, dhan_zones = zone_keys(left), zone_keys(right)
    return {
        "symbol": symbol,
        "common_candles": len(dates),
        "identical_candles": int(identical.sum()),
        "identical_percent": round(float(identical.mean() * 100), 4),
        "ohlc_different": int((~identical).sum()),
        "max_ohlc_difference": round(float(absolute.max().max()), 6),
        "yahoo_zones": len(yahoo_zones),
        "dhan_zones": len(dhan_zones),
        "zones_identical": len(yahoo_zones & dhan_zones),
        "zones_added_dhan": len(dhan_zones - yahoo_zones),
        "zones_removed_dhan": len(yahoo_zones - dhan_zones),
    }


def query_benchmarks(store: DhanShadowStore) -> dict[str, float]:
    statements = {
        "first_page": "SELECT * FROM dhan_instruments ORDER BY symbol LIMIT 25",
        "page_20": "SELECT * FROM dhan_instruments ORDER BY symbol LIMIT 25 OFFSET 475",
        "nse_filter": (
            "SELECT * FROM dhan_instruments WHERE category='NSE_MAIN' "
            "ORDER BY symbol LIMIT 25"
        ),
        "symbol_search": (
            "SELECT * FROM dhan_instruments WHERE symbol LIKE 'REL%' "
            "ORDER BY symbol LIMIT 25"
        ),
    }
    timings: dict[str, float] = {}
    with store.connection() as connection:
        for name, query in statements.items():
            started = perf_counter()
            connection.execute(query).fetchall()
            timings[name] = round((perf_counter() - started) * 1000, 4)
    return timings


def main() -> None:
    load_dotenv()
    dhan = DhanMarketDataProvider()
    comparisons: list[dict[str, object]] = []
    for symbol in ("RELIANCE", "TCS", "HDFCBANK", "INFY", "TMPV"):
        try:
            comparisons.append(compare(symbol, dhan))
        except Exception as error:
            comparisons.append({"symbol": symbol, "error": type(error).__name__})
    store = DhanShadowStore()
    print(
        json.dumps(
            {
                "comparison": comparisons,
                "query_latency_ms": query_benchmarks(store),
                "database_bytes": store.path.stat().st_size,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
