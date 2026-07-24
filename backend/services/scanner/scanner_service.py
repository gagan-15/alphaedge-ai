"""
Scanner Service.

Sprint:
    2.64 - Scanner Results Foundation
"""

from backend.config.market_scanner_config import (
    MarketScannerConfig,
)
from backend.config.entry_confirmation_config import (
    EntryConfirmationConfig,
)
from backend.config.risk_management_config import (
    RiskManagementConfig,
)
from backend.config.scanner_config import (
    ScannerConfig,
)
from backend.engines.entry_confirmation.entry_confirmation_engine import (
    EntryConfirmationEngine,
)
from backend.engines.market_scanner.market_scanner_engine import (
    MarketScannerEngine,
)
from backend.engines.risk_management_engine.risk_management_engine import (
    RiskManagementEngine,
)
from backend.models.market_scanner.market_scanner_result import (
    MarketScannerResult,
)
from backend.models.screener.screened_opportunity import (
    ScreenedOpportunity,
)
from backend.models.screener.screener_result import (
    ScreenerResult,
)
from backend.models.trade_setup.trade_setup import (
    TradeSetup,
)
from backend.models.zone import (
    Zone,
    ZoneType,
)
from backend.validators.scanner_validator import (
    ScannerValidator,
)


class ScannerService:
    """
    Provides scanner data.
    """

    def __init__(
        self,
        config: ScannerConfig | None = None,
    ) -> None:
        """
        Initialize the Scanner Service.
        """

        self._config = config or ScannerConfig()

        ScannerValidator.validate_config(
            self._config,
        )

        self._market_scanner_engine = MarketScannerEngine(
            MarketScannerConfig(),
        )
        self._entry_confirmation_engine = (
            EntryConfirmationEngine(
                EntryConfirmationConfig(),
            )
        )
        self._risk_management_engine = (
            RiskManagementEngine(
                RiskManagementConfig(),
            )
        )

    def get_scanner(
        self,
    ) -> MarketScannerResult:
        """
        Return the current scanner data.

        Controlled sample opportunities are used until
        live market analysis is integrated.
        """

        opportunities = [
            self._build_sample_opportunity(
                symbol="INFY",
                entry_price=1642.50,
                stop_loss=1602.50,
                target_price=1722.50,
                confirmation_score=92.0,
            ),
            self._build_sample_opportunity(
                symbol="TCS",
                entry_price=3980.75,
                stop_loss=3920.75,
                target_price=4100.75,
                confirmation_score=88.0,
            ),
        ]

        return self._market_scanner_engine.scan(
            symbols=list(self._config.symbols),
            screener_result=ScreenerResult(
                opportunities=opportunities,
            ),
        )

    def _build_sample_opportunity(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        target_price: float,
        confirmation_score: float,
    ) -> ScreenedOpportunity:
        """
        Build a deterministic sample opportunity.
        """

        trade_setup = TradeSetup(
            zone=Zone(
                zone_type=ZoneType.DEMAND,
                upper_price=entry_price,
                lower_price=stop_loss,
                created_index=0,
            ),
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price,
            risk_reward_ratio=(
                (target_price - entry_price)
                / (entry_price - stop_loss)
            ),
            is_buy=True,
        )

        confirmation = (
            self._entry_confirmation_engine.confirm(
                trade_setup=trade_setup,
                volume_confirmed=True,
                trend_confirmed=True,
                momentum_confirmed=True,
                confirmation_score=confirmation_score,
            )
        )

        risk_result = self._risk_management_engine.evaluate(
            entry_confirmation=confirmation,
            account_balance=self._config.account_balance,
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            target_price=target_price,
        )

        return ScreenedOpportunity(
            symbol=symbol,
            risk_management_result=risk_result,
        )
