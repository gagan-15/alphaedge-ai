"""
Portfolio Engine.

Sprint:
    2.43 - Portfolio Engine
"""

from backend.config.portfolio_config import (
    PortfolioConfig,
)
from backend.models.portfolio.portfolio_result import (
    PortfolioResult,
)
from backend.validators.portfolio_validator import (
    PortfolioValidator,
)


class PortfolioEngine:
    """
    Maintains the portfolio state.
    """

    def __init__(
        self,
        config: PortfolioConfig,
    ) -> None:
        """
        Initialize the Portfolio Engine.
        """
        PortfolioValidator.validate_config(config)

        self._config = config

    def update(
        self,
        total_positions: int,
        invested_capital: float,
    ) -> PortfolioResult:
        """
        Produce the current portfolio state.
        """

        available_capital = self._config.initial_capital - invested_capital

        if not self._config.allow_negative_balance and available_capital < 0:
            available_capital = 0.0

        return PortfolioResult(
            total_positions=total_positions,
            invested_capital=invested_capital,
            available_capital=available_capital,
            total_capital=self._config.initial_capital,
        )
