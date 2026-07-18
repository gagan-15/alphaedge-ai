"""
Tests for Dashboard Engine.

Sprint:
    2.45 - Dashboard Backend API
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


def test_engine_initializes() -> None:
    """
    Engine initializes successfully.
    """

    engine = DashboardEngine(
        DashboardConfig(),
    )

    assert engine is not None


def test_build_dashboard() -> None:
    """
    DashboardResult is built successfully.
    """

    engine = DashboardEngine(
        DashboardConfig(),
    )

    portfolio = PortfolioResult(
        total_positions=3,
        invested_capital=25000,
        available_capital=75000,
        total_capital=100000,
    )

    alerts = (
        AlertResult(
            title="BUY",
            message="INFY BUY",
            priority=AlertPriority.HIGH,
            requires_action=True,
        ),
    )

    scanner = MarketScannerResult(
        scanned_symbols=100,
        screener_result=ScreenerResult(
            opportunities=[],
        ),
    )

    backtest = BacktestResult(
        total_trades=100,
        winning_trades=70,
        losing_trades=30,
        win_rate=70.0,
    )

    ai = AIExplanationResult(
        decision=AIExplanationDecision.BUY,
        reasons=("Weekly Demand",),
        confidence_score=92.0,
        summary="Weekly Demand",
    )

    result = engine.build(
        portfolio=portfolio,
        alerts=alerts,
        scanner=scanner,
        backtest=backtest,
        ai_explanation=ai,
    )

    assert isinstance(
        result,
        DashboardResult,
    )

    assert result.portfolio == portfolio
    assert result.alerts == alerts
    assert result.scanner == scanner
    assert result.backtest == backtest
    assert result.ai_explanation == ai
