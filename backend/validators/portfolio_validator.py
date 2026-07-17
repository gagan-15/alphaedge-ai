"""
Portfolio validator.

Sprint:
    2.43 - Portfolio Engine
"""

from backend.config.portfolio_config import (
    PortfolioConfig,
)


class PortfolioValidator:
    """
    Validator for the Portfolio Engine.
    """

    @staticmethod
    def validate_config(
        config: PortfolioConfig,
    ) -> None:
        """
        Validate Portfolio configuration.
        """

        if config.initial_capital <= 0:
            raise ValueError("Initial capital must be greater than zero.")
