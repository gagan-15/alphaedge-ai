"""
Screener validator.

Sprint:
    2.39 - Screener Engine
"""

from backend.config.screener_config import (
    ScreenerConfig,
)


class ScreenerValidator:
    """
    Validator for the Screener Engine.
    """

    @staticmethod
    def validate_config(
        config: ScreenerConfig,
    ) -> None:
        """
        Validate Screener configuration.
        """

        if config.maximum_results <= 0:
            raise ValueError("Maximum results must be greater than zero.")
