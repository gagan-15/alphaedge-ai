"""
Portfolio configuration.

Sprint:
    2.43 - Portfolio Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioConfig:
    """
    Configuration for the Portfolio Engine.
    """

    initial_capital: float = 100000.0

    allow_negative_balance: bool = False
