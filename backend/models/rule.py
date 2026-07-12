"""
Rule model for AlphaEdge AI.

Sprint:
    2.22 - Rule Builder
"""

from dataclasses import dataclass

from backend.models.trading_signal import TradingSignal


@dataclass
class Rule:
    """
    Represents a single trading rule.
    """

    name: str
    passed: bool
    signal: TradingSignal
    reason: str