"""
Risk Management validator.

Sprint:
    2.38 - Risk Management Engine
"""

from backend.config.risk_management_config import (
    RiskManagementConfig,
)


class RiskManagementValidator:
    """
    Validator for the
    Risk Management Engine.
    """

    @staticmethod
    def validate_config(
        config: RiskManagementConfig,
    ) -> None:
        """
        Validate Risk Management
        configuration.
        """

        if config.risk_per_trade_percent <= 0:
            raise ValueError("Risk per trade percent must be greater than zero.")

        if config.minimum_risk_reward_ratio <= 0:
            raise ValueError("Minimum risk reward ratio must be greater than zero.")

        if (
            config.maximum_capital_per_trade_percent <= 0
            or config.maximum_capital_per_trade_percent > 100
        ):
            raise ValueError(
                "Maximum capital per trade percent must be between 0 and 100."
            )
