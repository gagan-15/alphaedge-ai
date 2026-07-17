"""
Backtest Result model.

Sprint:
    2.41 - Backtesting Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestResult:
    """
    Represents the result of a strategy backtest.
    """

    total_trades: int

    winning_trades: int

    losing_trades: int

    win_rate: float
