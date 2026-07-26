"""Real, delayed-data analysis for the Scanner Stock Details workspace."""

from __future__ import annotations

from typing import Any

import pandas as pd

from backend.config.sector_benchmark_config import (
    NIFTY_BENCHMARK,
    SECTOR_BENCHMARKS,
)
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.engines.zone_scoring_engine.zone_scoring_engine import ZoneScoringEngine
from backend.models.zone import Zone, ZoneType
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.market_data.timeframe_service import aggregate_timeframe


class StockDetailsAnalysisService:
    """Build benchmark, timeframe and direction-aware trade-plan context."""

    def __init__(self) -> None:
        self._market = MarketDataService()
        self._zones = ZoneDetectionEngine()
        self._scores = ZoneScoringEngine()

    @staticmethod
    def _returns(stock: pd.Series, benchmark: pd.Series) -> dict[str, Any]:
        joined = pd.concat(
            [stock.rename("stock"), benchmark.rename("benchmark")],
            axis=1,
            join="inner",
        ).dropna()
        periods = {"1m": 21, "3m": 63, "6m": 126}
        result: dict[str, Any] = {}
        for label, bars in periods.items():
            if len(joined) <= bars:
                result[label] = {"status": "INSUFFICIENT_HISTORY"}
                continue
            stock_return = (
                joined["stock"].iloc[-1] / joined["stock"].iloc[-bars - 1] - 1
            ) * 100
            benchmark_return = (
                joined["benchmark"].iloc[-1] / joined["benchmark"].iloc[-bars - 1] - 1
            ) * 100
            difference = stock_return - benchmark_return
            result[label] = {
                "stock_return": round(float(stock_return), 2),
                "benchmark_return": round(float(benchmark_return), 2),
                "difference": round(float(difference), 2),
                "status": (
                    "OUTPERFORMING"
                    if difference > 2
                    else "UNDERPERFORMING" if difference < -2 else "MATCHING"
                ),
            }
        return result

    @staticmethod
    def _ema(series: pd.Series, period: int) -> float | None:
        if len(series) < period:
            return None
        return float(series.ewm(span=period, adjust=False).mean().iloc[-1])

    def _timeframe(
        self, data: pd.DataFrame, label: str, demand: bool
    ) -> dict[str, Any]:
        framed = aggregate_timeframe(data, label)
        close = framed["Close"]
        ema20 = self._ema(close, 20)
        ema50 = self._ema(close, 50)
        if len(close) < 31:
            trend = "INSUFFICIENT_HISTORY"
        else:
            change = float(close.iloc[-1] / close.iloc[-31] - 1) * 100
            trend = "RISING" if change > 2 else "FALLING" if change < -2 else "SIDEWAYS"
        if ema20 is None or ema50 is None:
            alignment = "INSUFFICIENT_HISTORY"
        elif ema20 > ema50:
            alignment = "BULLISH"
        elif ema20 < ema50:
            alignment = "BEARISH"
        else:
            alignment = "MIXED"
        confirmed = trend == ("RISING" if demand else "FALLING") and alignment == (
            "BULLISH" if demand else "BEARISH"
        )
        return {
            "timeframe": label,
            "trend": trend,
            "ema_alignment": alignment,
            "confirmation": (
                "CONFIRMED"
                if confirmed
                else (
                    "NOT_CONFIRMED"
                    if trend != "INSUFFICIENT_HISTORY"
                    else "INSUFFICIENT_HISTORY"
                )
            ),
        }

    def _trade_plan(
        self,
        selected: Zone,
        all_zones: list[Zone],
        current_price: float,
    ) -> dict[str, Any]:
        demand = selected.zone_type == ZoneType.DEMAND
        width = selected.upper_price - selected.lower_price
        buffer = width * 0.10
        opposing = [
            zone
            for zone in all_zones
            if zone.zone_type != selected.zone_type
            and (
                zone.lower_price > selected.upper_price
                if demand
                else zone.upper_price < selected.lower_price
            )
        ]
        opposing.sort(
            key=lambda zone: zone.lower_price if demand else -zone.upper_price
        )
        nearest = opposing[0] if opposing else None
        entry = selected.upper_price if demand else selected.lower_price
        stop = (
            selected.lower_price - buffer if demand else selected.upper_price + buffer
        )
        target = (
            nearest.lower_price
            if demand and nearest
            else nearest.upper_price if nearest else None
        )
        risk = abs(entry - stop)
        reward = abs(target - entry) if target is not None else None
        ratio = reward / risk if reward is not None and risk > 0 else None
        distance = abs(current_price - entry) / current_price * 100
        return {
            "entry_range": [
                round(selected.lower_price, 2),
                round(selected.upper_price, 2),
            ],
            "illustrative_entry": round(entry, 2),
            "invalidation_stop": round(stop, 2),
            "stop_buffer_rule": "10% of zone width beyond the distal line",
            "target": round(target, 2) if target is not None else None,
            "target_basis": (
                "Nearest active opposing zone"
                if nearest
                else "No validated opposing zone found"
            ),
            "risk_per_share": round(risk, 2),
            "reward_per_share": round(reward, 2) if reward is not None else None,
            "risk_reward_ratio": round(ratio, 2) if ratio is not None else None,
            "distance_to_entry_percent": round(distance, 2),
            "research_only": True,
        }

    def build(
        self,
        symbol: str,
        zone_type: str,
        base_index: int,
    ) -> dict[str, Any]:
        stock = self._market.get_stock_data(symbol, period="10y", interval="1d")
        nifty = self._market.get_stock_data(
            NIFTY_BENCHMARK, period="10y", interval="1d"
        )
        detected = self._zones.detect_zones(stock)
        selected = min(
            (zone for zone in detected if zone.zone_type.value == zone_type),
            key=lambda zone: abs(zone.created_index - base_index),
        )
        current_price = float(stock["Close"].iloc[-1])
        benchmark = self._returns(stock["Close"], nifty["Close"])
        sector_name, sector_symbol = SECTOR_BENCHMARKS.get(symbol, ("UNMAPPED", ""))
        sector: dict[str, Any]
        if sector_symbol:
            sector_data = self._market.get_stock_data(
                sector_symbol, period="10y", interval="1d"
            )
            sector = {
                "name": sector_name,
                "benchmark": sector_symbol,
                "comparison": self._returns(stock["Close"], sector_data["Close"]),
                "sector_vs_nifty": self._returns(sector_data["Close"], nifty["Close"]),
            }
        else:
            sector = {
                "name": "UNMAPPED",
                "benchmark": None,
                "status": "SECTOR_BENCHMARK_MAPPING_REQUIRED",
            }
        timeframes = [
            self._timeframe(stock, label, selected.zone_type == ZoneType.DEMAND)
            for label in ("1D", "1W", "1M")
        ]
        confirmed = sum(item["confirmation"] == "CONFIRMED" for item in timeframes)
        return {
            "symbol": symbol,
            "source": "Yahoo Finance delayed OHLCV",
            "nifty_comparison": benchmark,
            "sector": sector,
            "multi_timeframe": {
                "frames": timeframes,
                "status": (
                    "CONFIRMED"
                    if confirmed == len(timeframes)
                    else "MIXED" if confirmed else "NOT_CONFIRMED"
                ),
            },
            "trade_plan": self._trade_plan(selected, detected, current_price),
        }
