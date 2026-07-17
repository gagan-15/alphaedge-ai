"""
Tests for Screener Engine.

Sprint:
    2.39 - Screener Engine
"""

import pytest

from backend.config.screener_config import (
    ScreenerConfig,
)
from backend.engines.screener_engine.screener_engine import (
    ScreenerEngine,
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


def _create_screened_opportunity() -> ScreenedOpportunity:
    """
    Create a reusable screened opportunity.
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

    risk_management_result = RiskManagementResult(
        entry_confirmation=entry_confirmation,
        position_size=PositionSize(
            quantity=100,
            capital_required=10000.0,
            risk_amount=500.0,
        ),
        risk_reward_ratio=3.0,
        approved=True,
    )

    return ScreenedOpportunity(
        symbol="INFY",
        risk_management_result=risk_management_result,
    )


def test_engine_initializes() -> None:
    """
    Engine initializes successfully.
    """

    engine = ScreenerEngine(
        ScreenerConfig(),
    )

    assert engine is not None


def test_invalid_configuration() -> None:
    """
    Invalid configuration raises ValueError.
    """

    with pytest.raises(ValueError):
        ScreenerEngine(
            ScreenerConfig(
                maximum_results=0,
            ),
        )


def test_screen_returns_result() -> None:
    """
    Screen returns ScreenerResult.
    """

    engine = ScreenerEngine(
        ScreenerConfig(),
    )

    result = engine.screen(
        opportunities=[
            _create_screened_opportunity(),
        ],
    )

    assert isinstance(
        result,
        ScreenerResult,
    )

    assert len(result.opportunities) == 1
    assert result.opportunities[0].symbol == "INFY"
    assert result.opportunities[0].risk_management_result.approved is True


def test_screen_filters_rejected_opportunities() -> None:
    """
    Rejected opportunities are filtered out.
    """

    approved = _create_screened_opportunity()

    rejected = ScreenedOpportunity(
        symbol="TCS",
        risk_management_result=RiskManagementResult(
            entry_confirmation=approved.risk_management_result.entry_confirmation,
            position_size=approved.risk_management_result.position_size,
            risk_reward_ratio=1.0,
            approved=False,
            rejection_reason="Rejected",
        ),
    )

    engine = ScreenerEngine(
        ScreenerConfig(
            approved_trades_only=True,
        ),
    )

    result = engine.screen(
        opportunities=[
            approved,
            rejected,
        ],
    )

    assert len(result.opportunities) == 1
    assert result.opportunities[0].symbol == "INFY"


def test_screen_respects_maximum_results() -> None:
    """
    Maximum results configuration is respected.
    """

    opportunity = _create_screened_opportunity()

    engine = ScreenerEngine(
        ScreenerConfig(
            maximum_results=1,
        ),
    )

    result = engine.screen(
        opportunities=[
            opportunity,
            ScreenedOpportunity(
                symbol="TCS",
                risk_management_result=opportunity.risk_management_result,
            ),
        ],
    )

    assert len(result.opportunities) == 1
