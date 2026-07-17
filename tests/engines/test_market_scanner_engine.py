"""
Tests for Market Scanner Engine.

Sprint:
    2.40 - Market Scanner Engine
"""

import pytest

from backend.config.market_scanner_config import (
    MarketScannerConfig,
)
from backend.engines.market_scanner.market_scanner_engine import (
    MarketScannerEngine,
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
from backend.models.entry_confirmation.entry_confirmation import (
    EntryConfirmation,
)
from backend.models.risk_management.position_size import (
    PositionSize,
)
from backend.models.risk_management.risk_management_result import (
    RiskManagementResult,
)
from backend.models.trade_setup.trade_setup import (
    TradeSetup,
)
from backend.models.zone import (
    Zone,
    ZoneType,
)


def _create_screener_result() -> ScreenerResult:
    """
    Create a reusable ScreenerResult.
    """

    zone = Zone(
        zone_type=ZoneType.DEMAND,
        upper_price=105.0,
        lower_price=95.0,
        created_index=10,
    )

    trade_setup = TradeSetup(
        zone=zone,
        entry_price=100.0,
        stop_loss=95.0,
        target_price=115.0,
        risk_reward_ratio=3.0,
        is_buy=True,
    )

    entry_confirmation = EntryConfirmation(
        trade_setup=trade_setup,
        volume_confirmed=True,
        trend_confirmed=True,
        momentum_confirmed=True,
        confirmation_score=100.0,
        confirmed=True,
    )

    risk_result = RiskManagementResult(
        entry_confirmation=entry_confirmation,
        position_size=PositionSize(
            quantity=100,
            capital_required=10000.0,
            risk_amount=500.0,
        ),
        risk_reward_ratio=3.0,
        approved=True,
    )

    return ScreenerResult(
        opportunities=[
            ScreenedOpportunity(
                symbol="INFY",
                risk_management_result=risk_result,
            ),
        ],
    )


def test_engine_initializes() -> None:
    """
    Engine initializes successfully.
    """

    engine = MarketScannerEngine(
        MarketScannerConfig(),
    )

    assert engine is not None


def test_invalid_configuration() -> None:
    """
    Invalid configuration raises ValueError.
    """

    with pytest.raises(ValueError):
        MarketScannerEngine(
            MarketScannerConfig(
                maximum_symbols=0,
            ),
        )


def test_scan_returns_result() -> None:
    """
    Scan returns a MarketScannerResult.
    """

    engine = MarketScannerEngine(
        MarketScannerConfig(),
    )

    result = engine.scan(
        symbols=[
            "INFY",
            "TCS",
            "RELIANCE",
        ],
        screener_result=_create_screener_result(),
    )

    assert isinstance(
        result,
        MarketScannerResult,
    )

    assert result.scanned_symbols == 3
    assert len(result.screener_result.opportunities) == 1


def test_scan_respects_maximum_symbols() -> None:
    """
    Scanner respects maximum_symbols.
    """

    engine = MarketScannerEngine(
        MarketScannerConfig(
            maximum_symbols=2,
        ),
    )

    result = engine.scan(
        symbols=[
            "INFY",
            "TCS",
            "RELIANCE",
        ],
        screener_result=_create_screener_result(),
    )

    assert result.scanned_symbols == 2


def test_scan_empty_symbols() -> None:
    """
    Empty symbol list returns zero scanned symbols.
    """

    engine = MarketScannerEngine(
        MarketScannerConfig(),
    )

    result = engine.scan(
        symbols=[],
        screener_result=_create_screener_result(),
    )

    assert result.scanned_symbols == 0
    assert len(result.screener_result.opportunities) == 1
