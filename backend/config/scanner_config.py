"""
Scanner configuration.

Sprint:
    2.64 - Scanner Results Foundation
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScannerConfig:
    """
    Configuration for the Scanner Engine.
    """

    symbols: tuple[str, ...] = (
        "INFY",
        "TCS",
        "HDFCBANK",
        "RELIANCE",
    )

    account_balance: float = 100000.0
