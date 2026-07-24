"""
Tests for market-data-driven opportunity analysis.
"""

import pandas as pd

from backend.config.scanner_config import ScannerConfig
from backend.engines.demand_supply_engine.demand_supply_engine import (
    DemandSupplyEngine,
)
from backend.models.zone import Zone, ZoneType
from backend.services.indicator.indicator_service import IndicatorService
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.scanner.market_opportunity_service import (
    MarketOpportunityService,
)


class StubMarketDataService(MarketDataService):
    """
    Return fixed market data without calling a provider.
    """

    def __init__(
        self,
        market_data: pd.DataFrame,
    ) -> None:
        self._market_data = market_data

    def get_stock_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        return self._market_data.copy()


class StubDemandSupplyEngine(DemandSupplyEngine):
    """
    Return fixed zones for orchestration tests.
    """

    def __init__(
        self,
        zones: list[Zone],
    ) -> None:
        self._zones = zones

    def detect(
        self,
        market_data: pd.DataFrame,
    ) -> list[Zone]:
        return self._zones


class StubIndicatorService(IndicatorService):
    """
    Return successful deterministic confirmations.
    """

    def calculate_volume_confirmation(
        self,
        data: pd.DataFrame,
        period: int = 20,
    ) -> pd.DataFrame:
        result = data.copy()
        result["Volume_Confirmation"] = "High"
        return result

    def calculate_sma(
        self,
        data: pd.DataFrame,
        period: int = 20,
    ) -> pd.DataFrame:
        result = data.copy()
        result[f"SMA_{period}"] = result["Close"] - 1.0
        return result

    def calculate_rsi(
        self,
        data: pd.DataFrame,
        period: int = 14,
    ) -> pd.Series:
        return pd.Series(
            [60.0] * len(data),
            index=data.index,
        )


def build_market_data() -> pd.DataFrame:
    """
    Build valid market data with the current price near the test zone.
    """

    return pd.DataFrame(
        {
            "Open": [100.0] * 30,
            "High": [103.0] * 30,
            "Low": [99.0] * 30,
            "Close": [102.0] * 30,
            "Volume": [2000] * 30,
        },
        index=pd.date_range(
            "2026-01-01",
            periods=30,
            freq="D",
        ),
    )


def build_service(
    zones: list[Zone],
) -> MarketOpportunityService:
    """
    Build an offline opportunity service.
    """

    return MarketOpportunityService(
        market_data_service=StubMarketDataService(
            build_market_data(),
        ),
        config=ScannerConfig(),
        demand_supply_engine=StubDemandSupplyEngine(
            zones,
        ),
        indicator_service=StubIndicatorService(),
    )


def test_analyze_builds_confirmed_opportunity() -> None:
    """
    A nearby fresh demand zone produces a risk-checked opportunity.
    """

    service = build_service(
        [
            Zone(
                zone_type=ZoneType.DEMAND,
                upper_price=100.0,
                lower_price=95.0,
                created_index=10,
                strength=90.0,
                is_fresh=True,
            )
        ]
    )

    opportunity = service.analyze(
        "INFY",
    )

    assert opportunity is not None
    assert opportunity.symbol == "INFY"
    assert opportunity.risk_management_result.approved is True
    assert opportunity.risk_management_result.entry_confirmation.confirmed is True


def test_analyze_ignores_distant_zone() -> None:
    """
    A demand zone too far below the market is not shown.
    """

    service = build_service(
        [
            Zone(
                zone_type=ZoneType.DEMAND,
                upper_price=80.0,
                lower_price=75.0,
                created_index=10,
                strength=90.0,
                is_fresh=True,
            )
        ]
    )

    assert service.analyze("INFY") is None


def test_analyze_ignores_supply_zone() -> None:
    """
    Supply zones are excluded until short-trade risk support exists.
    """

    service = build_service(
        [
            Zone(
                zone_type=ZoneType.SUPPLY,
                upper_price=105.0,
                lower_price=100.0,
                created_index=10,
                strength=90.0,
                is_fresh=True,
            )
        ]
    )

    assert service.analyze("INFY") is None
