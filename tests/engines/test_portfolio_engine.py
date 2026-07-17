"""
Tests for Portfolio Engine.

Sprint:
    2.43 - Portfolio Engine
"""

import pytest

from backend.config.portfolio_config import (
    PortfolioConfig,
)
from backend.engines.portfolio.portfolio_engine import (
    PortfolioEngine,
)
from backend.models.portfolio.portfolio_result import (
    PortfolioResult,
)


def test_engine_initializes() -> None:
    """
    Engine initializes successfully.
    """

    engine = PortfolioEngine(
        PortfolioConfig(),
    )

    assert engine is not None


def test_invalid_configuration() -> None:
    """
    Invalid configuration raises ValueError.
    """

    with pytest.raises(ValueError):
        PortfolioEngine(
            PortfolioConfig(
                initial_capital=0,
            ),
        )


def test_update_returns_result() -> None:
    """
    Update returns PortfolioResult.
    """

    engine = PortfolioEngine(
        PortfolioConfig(),
    )

    result = engine.update(
        total_positions=3,
        invested_capital=25000,
    )

    assert isinstance(
        result,
        PortfolioResult,
    )

    assert result.total_positions == 3
    assert result.invested_capital == 25000
    assert result.available_capital == 75000
    assert result.total_capital == 100000


def test_negative_balance_not_allowed() -> None:
    """
    Available capital is clamped to zero.
    """

    engine = PortfolioEngine(
        PortfolioConfig(),
    )

    result = engine.update(
        total_positions=5,
        invested_capital=120000,
    )

    assert result.available_capital == 0.0


def test_negative_balance_allowed() -> None:
    """
    Negative balances are allowed when configured.
    """

    engine = PortfolioEngine(
        PortfolioConfig(
            allow_negative_balance=True,
        ),
    )

    result = engine.update(
        total_positions=5,
        invested_capital=120000,
    )

    assert result.available_capital == -20000
