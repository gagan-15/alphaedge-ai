"""
Tests for Backtesting Engine.

Sprint:
    2.41 - Backtesting Engine
"""

import pytest

from backend.config.backtesting_config import (
    BacktestingConfig,
)
from backend.engines.backtesting.backtesting_engine import (
    BacktestingEngine,
)
from backend.models.backtesting.backtest_result import (
    BacktestResult,
)


def test_engine_initializes() -> None:
    """
    Engine initializes successfully.
    """

    engine = BacktestingEngine(
        BacktestingConfig(),
    )

    assert engine is not None


def test_invalid_configuration() -> None:
    """
    Invalid configuration raises ValueError.
    """

    with pytest.raises(ValueError):
        BacktestingEngine(
            BacktestingConfig(
                minimum_trades=0,
            ),
        )


def test_backtest_returns_result() -> None:
    """
    Backtest returns BacktestResult.
    """

    engine = BacktestingEngine(
        BacktestingConfig(),
    )

    result = engine.backtest(
        [
            True,
            True,
            False,
            True,
        ],
    )

    assert isinstance(
        result,
        BacktestResult,
    )

    assert result.total_trades == 4
    assert result.winning_trades == 3
    assert result.losing_trades == 1
    assert result.win_rate == 75.0


def test_empty_backtest() -> None:
    """
    Empty trade history returns zero metrics.
    """

    engine = BacktestingEngine(
        BacktestingConfig(),
    )

    result = engine.backtest([])

    assert result.total_trades == 0
    assert result.winning_trades == 0
    assert result.losing_trades == 0
    assert result.win_rate == 0.0


def test_all_losing_trades() -> None:
    """
    All losing trades produce zero win rate.
    """

    engine = BacktestingEngine(
        BacktestingConfig(),
    )

    result = engine.backtest(
        [
            False,
            False,
            False,
        ],
    )

    assert result.total_trades == 3
    assert result.winning_trades == 0
    assert result.losing_trades == 3
    assert result.win_rate == 0.0
