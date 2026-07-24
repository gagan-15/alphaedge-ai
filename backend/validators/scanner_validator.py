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
