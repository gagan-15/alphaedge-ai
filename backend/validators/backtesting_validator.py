"""
Backtesting validator.

Sprint:
    2.41 - Backtesting Engine
"""

from backend.config.backtesting_config import (
    BacktestingConfig,
)


class BacktestingValidator:
    """
    Validator for the Backtesting Engine.
    """

    @staticmethod
    def validate_config(
        config: BacktestingConfig,
    ) -> None:
        """
        Validate Backtesting configuration.
        """

        if config.minimum_trades <= 0:
            raise ValueError("Minimum trades must be greater than zero.")
