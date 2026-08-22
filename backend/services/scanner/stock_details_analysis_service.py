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
from backend.engines.trade_planning_engine import CanonicalTradePlanningEngine
from backend.engines.zone_scoring_engine.zone_scoring_engine import ZoneScoringEngine
from backend.config.canonical_methodology import SCANNER_METHODOLOGY_CACHE_VERSION
from backend.models.canonical_trade_plan import CanonicalPlanningZone
from backend.models.zone import Zone, ZoneType
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.market_data.timeframe_service import (
    INTRADAY_SOURCES,
    aggregate_timeframe,
)
from backend.services.scanner.canonical_trend_service import CanonicalTrendService
from backend.services.scanner.zone_lifecycle_ui_service import ZoneLifecycleUiService


class StockDetailsAnalysisService:
    """Build benchmark, timeframe and direction-aware trade-plan context."""

    def __init__(self) -> None:
        self._market = MarketDataService()
        self._zones = ZoneDetectionEngine()
        self._scores = ZoneScoringEngine()
        self._trend = CanonicalTrendService(self._market)
        self._lifecycle = ZoneLifecycleUiService()
        self._trade_planning = CanonicalTradePlanningEngine()

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

    def _trade_plan(
        self,
        selected: Zone,
        all_zones: list[Zone],
        data: pd.DataFrame,
        symbol: str,
        timeframe: str,
        current_price: float,
    ) -> dict[str, Any]:
        """Build the plan from same-snapshot canonical engine outputs only."""

        metadata = self._lifecycle.evaluate(
            all_zones,
            data,
            symbol=symbol,
            timeframe=timeframe,
            current_price=current_price,
        )
        snapshot_id = f"{symbol}:{timeframe}:{len(data)}:{data.index[-1].isoformat()}"

        def planning_zone(zone: Zone) -> CanonicalPlanningZone:
            facts = metadata[zone.created_index]
            demand = zone.zone_type == ZoneType.DEMAND
            return CanonicalPlanningZone(
                zone_id=facts.zone_id,
                symbol=symbol,
                timeframe=timeframe,
                snapshot_id=snapshot_id,
                methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
                zone_type=zone.zone_type.value,
                proximal=zone.upper_price if demand else zone.lower_price,
                distal=zone.lower_price if demand else zone.upper_price,
                formation_evidence_available=zone.formation_evidence is not None,
                authenticity_status=facts.authenticity_status,
                lifecycle_status=facts.lifecycle_status,
                is_active=not facts.is_invalidated,
                is_removed=facts.lifecycle_status == "REMOVED",
            )

        candidates = tuple(planning_zone(zone) for zone in all_zones)
        selected_input = planning_zone(selected)
        return self._trade_planning.build(
            selected_input,
            candidates,
            expected_snapshot_id=snapshot_id,
            expected_methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
        ).as_dict()

    def build(
        self,
        symbol: str,
        zone_type: str,
        proximal_price: float,
        distal_price: float,
        timeframe: str,
    ) -> dict[str, Any]:
        stock = self._market.get_stock_data(symbol, period="10y", interval="1d")
        nifty = self._market.get_stock_data(
            NIFTY_BENCHMARK, period="10y", interval="1d"
        )
        if timeframe in INTRADAY_SOURCES:
            source_period, source_interval = INTRADAY_SOURCES[timeframe]
            analysis_source = self._market.get_stock_data(
                symbol,
                period=source_period,
                interval=source_interval,
            )
        else:
            analysis_source = stock
        analysis_data = aggregate_timeframe(analysis_source, timeframe)
        detected = self._zones.detect_zones(analysis_data)
        selected = self._select_canonical_zone(
            detected,
            zone_type,
            proximal_price,
            distal_price,
        )
        current_price = float(analysis_data["Close"].iloc[-1])
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
        workflow, canonical_trend = self._trend.analyze(symbol, timeframe)
        alignment = self._trend.alignment(
            selected.zone_type.value, canonical_trend.trend_state
        ).value
        confirmation = (
            "CONFIRMED"
            if alignment == "ALIGNED"
            else "INSUFFICIENT_HISTORY" if alignment == "UNKNOWN" else "NOT_CONFIRMED"
        )
        timeframes = [
            {
                "timeframe": workflow.trend,
                "trend": canonical_trend.trend_state.value,
                "ema_alignment": "NOT_APPLICABLE_CANONICAL_TREND",
                "confirmation": confirmation,
                "canonical_trend": canonical_trend.as_dict(),
            }
        ]
        trade_plan = self._trade_plan(
            selected,
            detected,
            analysis_data,
            symbol,
            timeframe,
            current_price,
        )
        return {
            "symbol": symbol,
            "selected_zone": {
                "symbol": symbol,
                "zone_type": zone_type,
                "proximal_price": proximal_price,
                "distal_price": distal_price,
                "timeframe": timeframe,
            },
            "source": "Yahoo Finance delayed OHLCV",
            "nifty_comparison": benchmark,
            "sector": sector,
            "multi_timeframe": {
                "frames": timeframes,
                "status": confirmation,
                "workflow": {
                    "location": workflow.location,
                    "trend": workflow.trend,
                    "execution": workflow.execution,
                    "source": workflow.source.value,
                },
            },
            "trade_plan": trade_plan,
        }

    @staticmethod
    def _select_canonical_zone(
        detected: list[Zone],
        zone_type: str,
        proximal_price: float,
        distal_price: float,
    ) -> Zone:
        """Resolve a request only to a zone accepted by the canonical engine."""

        requested_type = (
            ZoneType.DEMAND if zone_type == "DEMAND" else ZoneType.SUPPLY
        )
        requested_upper = max(proximal_price, distal_price)
        requested_lower = min(proximal_price, distal_price)
        tolerance = max(0.01, requested_upper * 1e-6)
        selected = next(
            (
                zone
                for zone in detected
                if zone.zone_type == requested_type
                and abs(zone.upper_price - requested_upper) <= tolerance
                and abs(zone.lower_price - requested_lower) <= tolerance
            ),
            None,
        )
        if selected is None:
            raise LookupError(
                "Selected zone is not valid under the current canonical methodology."
            )
        return selected
