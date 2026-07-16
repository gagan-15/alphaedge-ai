"""
Entry Confirmation model.

Sprint:
    2.37 - Entry Confirmation Engine
"""

from dataclasses import dataclass

from backend.models.trade_setup.trade_setup import (
    TradeSetup,
)


@dataclass(frozen=True)
class EntryConfirmation:
    """
    Represents a confirmed trade setup.
    """

    trade_setup: TradeSetup

    volume_confirmed: bool

    trend_confirmed: bool

    momentum_confirmed: bool

    confirmation_score: float

    confirmed: bool
