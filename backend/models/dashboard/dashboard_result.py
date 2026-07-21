"""
Dashboard Result model.

Sprint:
    2.45 - Dashboard Backend API
"""

from dataclasses import dataclass

from backend.models.ai_explanation.ai_explanation_result import (
    AIExplanationResult,
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
from backend.models.dashboard.market_overview_result import (
    MarketOverviewResult,
)

@dataclass(frozen=True)
class DashboardResult:
    """
    Represents all information required
    by the Dashboard.
    """
    market: MarketOverviewResult

    portfolio: PortfolioResult

    alerts: tuple[AlertResult, ...]

    scanner: MarketScannerResult

    backtest: BacktestResult

    ai_explanation: AIExplanationResult

