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

    account_balance: float = 100000.0

    period: str = "1y"

    interval: str = "1d"

    maximum_zone_distance_percent: float = 5.0

    volume_period: int = 20

    trend_period: int = 20

    momentum_period: int = 14

    minimum_momentum: float = 50.0

    maximum_momentum: float = 70.0

    scan_concurrency: int = 6

    # A reacting zone remains active until price has moved this far beyond
    # its proximal boundary. Supported research values: 2, 3, 5, 7, 10.
    reaction_completion_percent: float = 5.0

    def __post_init__(self) -> None:
        if self.reaction_completion_percent not in {2, 3, 5, 7, 10}:
            raise ValueError(
                "reaction_completion_percent must be 2, 3, 5, 7, or 10"
            )
