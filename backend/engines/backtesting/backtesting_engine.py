"""
Backtesting Engine.

Sprint:
    2.41 - Backtesting Engine
"""

from backend.config.backtesting_config import (
    BacktestingConfig,
)
from backend.models.backtesting.backtest_result import (
    BacktestResult,
)
from backend.validators.backtesting_validator import (
    BacktestingValidator,
)


class BacktestingEngine:
    """
    Evaluates historical trading results.
    """

    def __init__(
        self,
        config: BacktestingConfig,
    ) -> None:
        """
        Initialize the Backtesting Engine.
        """
        BacktestingValidator.validate_config(config)

        self._config = config

    def backtest(
        self,
        trade_results: list[bool],
    ) -> BacktestResult:
        """
        Evaluate historical trade results.

        True  = Winning trade
        False = Losing trade
        """

        total_trades = len(trade_results)

        winning_trades = sum(trade_results)

        losing_trades = total_trades - winning_trades

        if self._config.calculate_win_rate and total_trades > 0:
            win_rate = (winning_trades / total_trades) * 100
        else:
            win_rate = 0.0

        return BacktestResult(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
        )
