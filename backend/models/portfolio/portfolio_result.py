"""
Portfolio Result model.

Sprint:
    2.43 - Portfolio Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioResult:
    """
    Represents the current portfolio state.
    """

    total_positions: int

    invested_capital: float

    available_capital: float

    total_capital: float
