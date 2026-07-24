"""
Signals Result.

Sprint:
    2.61 - Signals Panel
"""

from dataclasses import dataclass


@dataclass(slots=True)
class SignalResult:
    """
    Represents a single trading signal shown on the dashboard.
    """

    symbol: str

    action: str

    price: float

    confidence: float
