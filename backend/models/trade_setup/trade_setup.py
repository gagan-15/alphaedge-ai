"""
Trade Setup model.

Sprint:
    2.36 - Trade Setup Engine
"""

from dataclasses import dataclass

from backend.models.zone import Zone


@dataclass(frozen=True)
class TradeSetup:
    """
    Represents a complete trade setup.
    """

    zone: Zone

    entry_price: float

    stop_loss: float

    target_price: float

    risk_reward_ratio: float

    is_buy: bool
