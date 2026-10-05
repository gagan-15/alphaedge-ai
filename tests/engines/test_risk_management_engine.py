"""
Tests for Risk Management Engine.

Sprint:
    2.38 - Risk Management Engine
"""

import pytest

from backend.config.risk_management_config import (
    RiskManagementConfig,
)
from backend.engines.risk_management_engine.risk_management_engine import (
    RiskManagementEngine,
)
from backend.models.entry_confirmation.entry_confirmation import (
    EntryConfirmation,
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


def _create_entry_confirmation() -> EntryConfirmation:
    """
    Create a reusable confirmed trade.
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

    return EntryConfirmation(
        trade_setup=trade_setup,
        volume_confirmed=True,
        trend_confirmed=True,
        momentum_confirmed=True,
        confirmation_score=100.0,
        confirmed=True,
    )


def test_engine_initializes() -> None:

    engine = RiskManagementEngine(
        RiskManagementConfig(),
    )

    assert engine is not None


def test_invalid_configuration() -> None:

    config = RiskManagementConfig(
        risk_per_trade_percent=0.0,
    )

    with pytest.raises(ValueError):
        RiskManagementEngine(config)


def test_trade_is_approved() -> None:

    engine = RiskManagementEngine(
        RiskManagementConfig(),
    )

    result = engine.evaluate(
        entry_confirmation=_create_entry_confirmation(),
        account_balance=1_000_000.0,
        entry_price=100.0,
        stop_loss_price=95.0,
        target_price=115.0,
    )

    assert isinstance(
        result,
        RiskManagementResult,
    )

    assert result.approved is True
    assert result.position_size.quantity == 2000
    assert result.risk_reward_ratio == 3.0


def test_trade_is_rejected() -> None:

    engine = RiskManagementEngine(
        RiskManagementConfig(),
    )

    result = engine.evaluate(
        entry_confirmation=_create_entry_confirmation(),
        account_balance=1_000_000.0,
        entry_price=100.0,
        stop_loss_price=95.0,
        target_price=105.0,
    )

    assert result.approved is False
    assert result.rejection_reason is not None


def test_unconfirmed_trade_is_rejected() -> None:
    """
    Good risk/reward cannot approve an unconfirmed entry.
    """

    engine = RiskManagementEngine(
        RiskManagementConfig(),
    )
    confirmed_entry = _create_entry_confirmation()
    unconfirmed_entry = EntryConfirmation(
        trade_setup=confirmed_entry.trade_setup,
        volume_confirmed=True,
        trend_confirmed=False,
        momentum_confirmed=True,
        confirmation_score=80.0,
        confirmed=False,
    )

    result = engine.evaluate(
        entry_confirmation=unconfirmed_entry,
        account_balance=1_000_000.0,
        entry_price=100.0,
        stop_loss_price=95.0,
        target_price=115.0,
    )

    assert result.approved is False
    assert result.rejection_reason == ("Entry confirmation requirements were not met.")


def test_invalid_stop_loss() -> None:

    engine = RiskManagementEngine(
        RiskManagementConfig(),
    )

    with pytest.raises(ValueError):
        engine.evaluate(
            entry_confirmation=_create_entry_confirmation(),
            account_balance=1_000_000.0,
            entry_price=100.0,
            stop_loss_price=100.0,
            target_price=120.0,
        )
