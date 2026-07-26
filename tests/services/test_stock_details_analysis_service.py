import pandas as pd

from backend.models.zone import Zone, ZoneType
from backend.services.scanner.stock_details_analysis_service import (
    StockDetailsAnalysisService,
)


def test_aligned_benchmark_returns_use_matching_dates() -> None:
    dates = pd.date_range("2025-01-01", periods=140, freq="B")
    stock = pd.Series(range(100, 240), index=dates, dtype=float)
    benchmark = pd.Series(range(100, 170), index=dates[::2], dtype=float)

    result = StockDetailsAnalysisService._returns(stock, benchmark)

    assert result["1m"]["status"] in {"OUTPERFORMING", "MATCHING", "UNDERPERFORMING"}
    assert "difference" in result["1m"]
    assert result["6m"]["status"] == "INSUFFICIENT_HISTORY"


def test_demand_trade_plan_uses_nearest_supply() -> None:
    service = StockDetailsAnalysisService()
    demand = Zone(ZoneType.DEMAND, 105, 100, 10)
    near_supply = Zone(ZoneType.SUPPLY, 125, 120, 30)
    far_supply = Zone(ZoneType.SUPPLY, 150, 145, 50)

    plan = service._trade_plan(demand, [demand, far_supply, near_supply], 112)

    assert plan["illustrative_entry"] == 105
    assert plan["invalidation_stop"] == 99.5
    assert plan["target"] == 120
    assert plan["risk_reward_ratio"] == 2.73
    assert plan["research_only"] is True


def test_supply_trade_plan_is_direction_aware() -> None:
    service = StockDetailsAnalysisService()
    supply = Zone(ZoneType.SUPPLY, 130, 125, 10)
    demand = Zone(ZoneType.DEMAND, 110, 105, 30)

    plan = service._trade_plan(supply, [supply, demand], 120)

    assert plan["illustrative_entry"] == 125
    assert plan["invalidation_stop"] == 130.5
    assert plan["target"] == 110
    assert plan["risk_reward_ratio"] == 2.73
