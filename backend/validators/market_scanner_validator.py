"""
Market Scanner validator.

Sprint:
    2.40 - Market Scanner Engine
"""

from backend.config.market_scanner_config import (
    MarketScannerConfig,
)


class MarketScannerValidator:
    """
    Validator for the Market Scanner Engine.
    """

    @staticmethod
    def validate_config(
        config: MarketScannerConfig,
    ) -> None:
        """
        Validate Market Scanner configuration.
        """

        if config.maximum_symbols <= 0:
            raise ValueError("Maximum symbols must be greater than zero.")
