"""
Market Scanner Result model.

Sprint:
    2.40 - Market Scanner Engine
"""

from dataclasses import dataclass

from backend.models.screener.screener_result import (
    ScreenerResult,
)


@dataclass(frozen=True)
class MarketScannerResult:
    """
    Represents the result returned by the
    Market Scanner Engine.
    """

    scanned_symbols: int

    screener_result: ScreenerResult
