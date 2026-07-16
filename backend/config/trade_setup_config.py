"""
Trade Setup Configuration.

Sprint:
    2.36 - Trade Setup Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TradeSetupConfig:
    """
    Configuration for Trade Setup Engine.
    """

    entry_buffer_percentage: float = 0.10

    stop_buffer_percentage: float = 0.10

    minimum_risk_reward: float = 2.0

    use_zone_midpoint_entry: bool = False

    enable_buy_setups: bool = True

    enable_sell_setups: bool = True
