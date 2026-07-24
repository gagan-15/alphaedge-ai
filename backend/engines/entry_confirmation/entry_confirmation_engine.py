"""
Entry Confirmation Engine.

Sprint:
    2.37 - Entry Confirmation Engine
"""

from backend.config.entry_confirmation_config import (
    EntryConfirmationConfig,
)
from backend.models.entry_confirmation.entry_confirmation import (
    EntryConfirmation,
)
from backend.models.trade_setup.trade_setup import (
    TradeSetup,
)
from backend.validators.entry_confirmation_validator import (
    EntryConfirmationValidator,
)


class EntryConfirmationEngine:
    """
    Validates trade confirmation before
    risk management.
    """

    def __init__(
        self,
        config: EntryConfirmationConfig,
    ) -> None:
        """
        Initialize the engine.
        """

        EntryConfirmationValidator.validate_config(
            config,
        )

        self._config = config

    def confirm(
        self,
        trade_setup: TradeSetup,
        volume_confirmed: bool,
        trend_confirmed: bool,
        momentum_confirmed: bool,
        confirmation_score: float,
    ) -> EntryConfirmation:
        """
        Produce an EntryConfirmation result.
        """

        confirmed = (
            volume_confirmed
            and trend_confirmed
            and momentum_confirmed
            and confirmation_score
            >= self._config.minimum_confirmation_score
        )

        return EntryConfirmation(
            trade_setup=trade_setup,
            volume_confirmed=volume_confirmed,
            trend_confirmed=trend_confirmed,
            momentum_confirmed=momentum_confirmed,
            confirmation_score=confirmation_score,
            confirmed=confirmed,
        )
