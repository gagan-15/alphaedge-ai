"""
Dashboard Service.

Sprint:
    2.47 - Dashboard Service
"""

from backend.config.dashboard_config import (
    DashboardConfig,
)
from backend.engines.dashboard.dashboard_engine import (
    DashboardEngine,
)
from backend.models.ai_explanation.ai_explanation_result import (
    AIExplanationResult,
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

    def build_dashboard(
        self,
        portfolio: PortfolioResult,
        alerts: tuple[AlertResult, ...],
        scanner: MarketScannerResult,
        backtest: BacktestResult,
        ai_explanation: AIExplanationResult,
    ) -> DashboardResult:
        """
        Build dashboard data.
        """

        return self._engine.build(
            portfolio=portfolio,
            alerts=alerts,
            scanner=scanner,
            backtest=backtest,
            ai_explanation=ai_explanation,
        )
