"""
Dashboard API.

Sprint:
    2.47 - Dashboard API
"""

from fastapi import APIRouter

from backend.models.ai_explanation.ai_explanation_decision import (
    AIExplanationDecision,
)
from backend.models.ai_explanation.ai_explanation_result import (
    AIExplanationResult,
)
from backend.models.alert.alert_priority import (
    AlertPriority,
)
from backend.models.alert.alert_result import (
    AlertResult,
)
from backend.models.backtesting.backtest_result import (
    BacktestResult,
)
from backend.models.market_scanner.market_scanner_result import (
    MarketScannerResult,
)
from backend.models.portfolio.portfolio_result import (
    PortfolioResult,
)
from backend.models.screener.screener_result import (
    ScreenerResult,
)
from backend.services.dashboard.dashboard_service import (
    DashboardService,
)

dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@dashboard_router.get("/")
def get_dashboard():
    """
    Return dashboard data.
    """

    service = DashboardService()

    dashboard = service.build_dashboard(
        portfolio=PortfolioResult(
            total_positions=3,
            invested_capital=25000,
            available_capital=75000,
            total_capital=100000,
        ),
        alerts=(
            AlertResult(
                title="BUY",
                message="INFY BUY",
                priority=AlertPriority.HIGH,
                requires_action=True,
            ),
        ),
        scanner=MarketScannerResult(
            scanned_symbols=100,
            screener_result=ScreenerResult(
                opportunities=[],
            ),
        ),
        backtest=BacktestResult(
            total_trades=100,
            winning_trades=70,
            losing_trades=30,
            win_rate=70.0,
        ),
        ai_explanation=AIExplanationResult(
            decision=AIExplanationDecision.BUY,
            reasons=("Weekly Demand Zone",),
            confidence_score=92.0,
            summary="Weekly Demand Zone",
        ),
    )

    return dashboard
