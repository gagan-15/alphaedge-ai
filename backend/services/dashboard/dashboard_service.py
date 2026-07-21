"""
Dashboard Service.

Sprint:
    2.48 - Dashboard Service Enhancement
"""

from backend.config.dashboard_config import (
    DashboardConfig,
)
from backend.engines.dashboard.dashboard_engine import (
    DashboardEngine,
)
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
from backend.models.dashboard.dashboard_result import (
    DashboardResult,
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
from backend.models.dashboard.market_overview_result import (
    MarketOverviewResult,
)


class DashboardService:
    """
    Provides dashboard data.
    """

    def __init__(self) -> None:
        """
        Initialize the Dashboard Service.
        """

        self._engine = DashboardEngine(
            DashboardConfig(),
        )

    def get_dashboard(self) -> DashboardResult:
        """
        Return the current dashboard data.

        Sample data is used temporarily until live
        application services are integrated.
        """

        return self._engine.build(
            market=MarketOverviewResult(
            nifty50=24731.45,
            nifty_change=0.85,
            sensex=81214.85,
            sensex_change=0.78,
            bank_nifty=54372.15,
            bank_nifty_change=1.15,
            india_vix=12.45,
            india_vix_change=-2.35,
            ),
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
