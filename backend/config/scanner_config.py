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

    period: str = "1y"

    interval: str = "1d"

    maximum_zone_distance_percent: float = 5.0

    volume_period: int = 20

    trend_period: int = 20

    momentum_period: int = 14

    minimum_momentum: float = 50.0

    maximum_momentum: float = 70.0
