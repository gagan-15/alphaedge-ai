"""
Screener configuration.

Sprint:
    2.39 - Screener Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScreenerConfig:
    """
    Configuration for the Screener Engine.
    """

    maximum_results: int = 20

    approved_trades_only: bool = True
