"""
Scanner validator.

Sprint:
    2.64 - Scanner Results Foundation
"""

from backend.config.scanner_config import (
    ScannerConfig,
)


class ScannerValidator:
    """
    Validator for Scanner configuration.
    """

    @staticmethod
    def validate_config(
        config: ScannerConfig,
    ) -> None:
        """
        Validate Scanner configuration.
        """

        if not isinstance(config, ScannerConfig):
            raise TypeError(
                "config must be a ScannerConfig.",
            )

        if not config.symbols:
            raise ValueError(
                "symbols cannot be empty.",
            )

        if config.account_balance <= 0:
            raise ValueError(
                "account_balance must be greater than zero.",
            )

        if config.maximum_zone_distance_percent < 0:
            raise ValueError(
                "maximum_zone_distance_percent cannot be negative.",
            )

        periods = (
            config.volume_period,
            config.trend_period,
            config.momentum_period,
        )

        if any(period <= 0 for period in periods):
            raise ValueError(
                "indicator periods must be greater than zero.",
            )

        if not 0 <= config.minimum_momentum < config.maximum_momentum <= 100:
            raise ValueError(
                "momentum range must be between zero and 100.",
            )
