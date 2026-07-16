"""
Entry Confirmation Validator.

Sprint:
    2.37 - Entry Confirmation Engine
"""

from backend.config.entry_confirmation_config import (
    EntryConfirmationConfig,
)
from backend.models.trade_setup.trade_setup import (
    TradeSetup,
)


class EntryConfirmationValidator:
    """
    Validate Entry Confirmation inputs.
    """

    @staticmethod
    def validate(
        trade_setups: list[TradeSetup],
        config: EntryConfirmationConfig,
    ) -> None:

        if not trade_setups:
            raise ValueError("trade_setups cannot be empty.")

        if (
            config.minimum_confirmation_score < 0
            or config.minimum_confirmation_score > 100
        ):
            raise ValueError("minimum_confirmation_score must be between 0 and 100.")
