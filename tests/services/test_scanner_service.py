"""
Tests for scanner orchestration and symbol error isolation.
"""

from backend.config.entry_confirmation_config import EntryConfirmationConfig
from backend.config.risk_management_config import RiskManagementConfig
from backend.config.scanner_config import ScannerConfig
from backend.engines.entry_confirmation.entry_confirmation_engine import (
    EntryConfirmationEngine,
)
from backend.engines.risk_management_engine.risk_management_engine import (
    RiskManagementEngine,
)
from backend.models.screener.screened_opportunity import ScreenedOpportunity
from backend.models.trade_setup.trade_setup import TradeSetup
from backend.models.zone import Zone, ZoneType
from backend.services.scanner.scanner_service import ScannerService


class StubOpportunityService:
    """
    Return one opportunity and fail one symbol.
    """

    def analyze(
        self,
        symbol: str,
    ) -> ScreenedOpportunity | None:
        if symbol == "FAILED":
            raise RuntimeError("Provider failed.")

        if symbol == "EMPTY":
            return None

        setup = TradeSetup(
            zone=Zone(
                zone_type=ZoneType.DEMAND,
                upper_price=100.0,
                lower_price=95.0,
                created_index=10,
            ),
            entry_price=100.0,
            stop_loss=95.0,
            target_price=110.0,
            risk_reward_ratio=2.0,
            is_buy=True,
        )
        confirmation = EntryConfirmationEngine(
            EntryConfirmationConfig(),
        ).confirm(
            trade_setup=setup,
            volume_confirmed=True,
            trend_confirmed=True,
            momentum_confirmed=True,
            confirmation_score=90.0,
        )
        risk_result = RiskManagementEngine(
            RiskManagementConfig(),
        ).evaluate(
            entry_confirmation=confirmation,
            account_balance=100000.0,
            entry_price=100.0,
            stop_loss_price=95.0,
            target_price=110.0,
        )

        return ScreenedOpportunity(
            symbol=symbol,
            risk_management_result=risk_result,
        )


def test_scanner_continues_after_symbol_failure() -> None:
    """
    One failed symbol does not stop the rest of the scan.
    """

    service = ScannerService(
        config=ScannerConfig(
            symbols=(
                "INFY",
                "FAILED",
                "EMPTY",
            ),
        ),
        opportunity_service=StubOpportunityService(),
    )

    result = service.get_scanner()

    assert result.scanned_symbols == 3
    assert len(result.screener_result.opportunities) == 1
    assert result.screener_result.opportunities[0].symbol == "INFY"
