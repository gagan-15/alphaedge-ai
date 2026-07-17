"""
Position Size model.

Sprint:
    2.38 - Risk Management Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PositionSize:
    """
    Represents the calculated position size for a trade.
    """

    quantity: int

    capital_required: float

    risk_amount: float
