"""
Dashboard Engine.

Sprint:
    2.45 - Dashboard Backend API
"""

from backend.config.dashboard_config import (
    DashboardConfig,
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
from backend.validators.dashboard_validator import (
    DashboardValidator,
)
from backend.models.dashboard.market_overview_result import (
    MarketOverviewResult,
)


class DashboardEngine:
    """
    Produces dashboard data.
    """

    def __init__(
        self,
        config: DashboardConfig,
    ) -> None:
        """
        Initialize the Dashboard Engine.
        """

        DashboardValidator.validate_config(
            config,
        )

        self._config = config

    def build(
        self,
        market: MarketOverviewResult,
        portfolio: PortfolioResult,
        alerts: tuple[AlertResult, ...],
        scanner: MarketScannerResult,
        backtest: BacktestResult,
        ai_explanation: AIExplanationResult,
    ) -> DashboardResult:
        """
        Build the dashboard result.
        """

        return DashboardResult(
            market=market,
            portfolio=portfolio,
            alerts=alerts,
            scanner=scanner,
            backtest=backtest,
            ai_explanation=ai_explanation,
        )
