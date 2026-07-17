"""
Backtesting configuration.

Sprint:
    2.41 - Backtesting Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestingConfig:
    """
    Configuration for the Backtesting Engine.
    """

    minimum_trades: int = 30

    calculate_win_rate: bool = True
