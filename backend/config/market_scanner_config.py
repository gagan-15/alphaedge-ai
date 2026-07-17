"""
Market Scanner configuration.

Sprint:
    2.40 - Market Scanner Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketScannerConfig:
    """
    Configuration for the Market Scanner Engine.
    """

    maximum_symbols: int = 500

    continue_on_error: bool = True
