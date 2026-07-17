"""
Risk Management Result model.

Sprint:
    2.38 - Risk Management Engine
"""

from dataclasses import dataclass

from backend.models.entry_confirmation.entry_confirmation import (
    EntryConfirmation,
)
from backend.models.risk_management.position_size import (
    PositionSize,
)


@dataclass(frozen=True)
class RiskManagementResult:
    """
    Represents the result produced by the Risk Management Engine.
    """

    entry_confirmation: EntryConfirmation

    position_size: PositionSize

    risk_reward_ratio: float

    approved: bool

    rejection_reason: str | None = None
