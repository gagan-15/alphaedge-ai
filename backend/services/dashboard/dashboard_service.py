"""
Dashboard Service.

Sprint:
    2.61 - Signals Panel
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
from backend.models.backtesting.backtest_result import (
    BacktestResult,
)
from backend.models.dashboard.dashboard_result import (
    DashboardResult,
)
from backend.models.dashboard.market_overview_result import (
    MarketOverviewResult,
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
from backend.services.market_data.market_snapshot_service import MarketSnapshotService
from backend.services.scanner.universe_service import UniverseName, UniverseService


class DashboardService:
    """
    Provides dashboard data.
    """

    def __init__(
        self,
        snapshot_service: MarketSnapshotService | None = None,
        universe_service: UniverseService | None = None,
    ) -> None:
        """
        Initialize the Dashboard Service.
        """

        self._engine = DashboardEngine(
            DashboardConfig(),
        )
        self._snapshot_service = snapshot_service or MarketSnapshotService()
        self._universe_service = universe_service or UniverseService()

    def get_dashboard(
        self,
        universe: UniverseName = "nse500",
        supplied_symbols: list[str] | None = None,
    ) -> DashboardResult:
        """
        Return the current dashboard data.

        Benchmark values and breadth come from the shared delayed market source.
        """
        snapshot = self._snapshot_service.get_snapshot(universe, supplied_symbols)
        symbols = self._universe_service.get_symbols(universe, supplied_symbols)

        def value(name: str) -> tuple[float, float]:
            quote = snapshot.quotes.get(name)
            return (quote.price, quote.change_percent) if quote else (0.0, 0.0)

        nifty, nifty_change = value("nifty50")
        sensex, sensex_change = value("sensex")
        bank_nifty, bank_nifty_change = value("bank_nifty")
        india_vix, india_vix_change = value("india_vix")
        breadth_total = snapshot.advancing + snapshot.declining + snapshot.unchanged
        participation = (
            snapshot.advancing / breadth_total * 100
            if breadth_total
            else 0.0
        )
        average_change = (nifty_change + sensex_change + bank_nifty_change) / 3
        decision = (
            AIExplanationDecision.BUY
            if average_change > 0.25 and participation >= 50
            else AIExplanationDecision.WAIT
        )

        return self._engine.build(
            market=MarketOverviewResult(
                nifty50=nifty,
                nifty_change=nifty_change,
                sensex=sensex,
                sensex_change=sensex_change,
                bank_nifty=bank_nifty,
                bank_nifty_change=bank_nifty_change,
                india_vix=india_vix,
                india_vix_change=india_vix_change,
                advancing=snapshot.advancing,
                declining=snapshot.declining,
                unchanged=snapshot.unchanged,
                total_symbols=snapshot.total_symbols,
                processed_symbols=snapshot.processed_symbols,
                source=snapshot.source,
                data_status=snapshot.data_status,
                updated_at=snapshot.updated_at.isoformat(),
            ),
            portfolio=PortfolioResult(
                total_positions=3,
                invested_capital=25000,
                available_capital=75000,
                total_capital=100000,
            ),
            signals=(),
            alerts=(),
            scanner=MarketScannerResult(
                scanned_symbols=len(symbols),
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
                decision=decision,
                reasons=(
                    (
                        f"{snapshot.advancing} of {breadth_total} processed "
                        "stocks are advancing."
                    ),
                ),
                confidence_score=round(min(95.0, max(0.0, participation)), 1),
                summary=(
                    "More stocks are rising than falling."
                    if participation >= 50
                    else "Market participation is mixed or still refreshing."
                ),
            ),
        )
