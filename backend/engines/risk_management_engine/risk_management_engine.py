"""
Risk Management Engine.

Sprint:
    2.38 - Risk Management Engine
"""

from backend.config.risk_management_config import (
    RiskManagementConfig,
)
from backend.models.entry_confirmation.entry_confirmation import (
    EntryConfirmation,
)
from backend.models.risk_management.position_size import (
    PositionSize,
)
from backend.models.risk_management.risk_management_result import (
    RiskManagementResult,
)
from backend.validators.risk_management_validator import (
    RiskManagementValidator,
)


class RiskManagementEngine:
    """
    Calculates position sizing and
    validates trade risk.
    """

    def __init__(
        self,
        config: RiskManagementConfig,
    ) -> None:
        """
        Initialize the engine.
        """
        RiskManagementValidator.validate_config(config)

        self._config = config

    def evaluate(
        self,
        entry_confirmation: EntryConfirmation,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        target_price: float,
    ) -> RiskManagementResult:
        """
        Evaluate trade risk and
        return the risk management result.
        """

        risk_per_share = entry_price - stop_loss_price

        if risk_per_share <= 0:
            raise ValueError("Entry price must be greater than stop loss price.")

        risk_amount = account_balance * self._config.risk_per_trade_percent / 100

        quantity = int(risk_amount / risk_per_share)

        capital_required = quantity * entry_price

        reward = target_price - entry_price

        risk_reward_ratio = reward / risk_per_share

        approved = risk_reward_ratio >= self._config.minimum_risk_reward_ratio

        rejection_reason = None

        if not approved:
            rejection_reason = "Risk reward ratio below minimum threshold."

        position_size = PositionSize(
            quantity=quantity,
            capital_required=capital_required,
            risk_amount=risk_amount,
        )

        return RiskManagementResult(
            entry_confirmation=entry_confirmation,
            position_size=position_size,
            risk_reward_ratio=risk_reward_ratio,
            approved=approved,
            rejection_reason=rejection_reason,
        )
