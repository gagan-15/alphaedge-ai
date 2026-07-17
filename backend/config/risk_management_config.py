"""
Risk Management configuration.

Sprint:
    2.38 - Risk Management Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskManagementConfig:
    """
    Configuration for the
    Risk Management Engine.
    """

    risk_per_trade_percent: float = 1.0

    minimum_risk_reward_ratio: float = 2.0

    maximum_capital_per_trade_percent: float = 20.0
