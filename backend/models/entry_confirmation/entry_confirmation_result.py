"""
Entry Confirmation Result.

Sprint:
    2.37 - Entry Confirmation Engine
"""

from dataclasses import dataclass, field

from backend.models.entry_confirmation.entry_confirmation import (
    EntryConfirmation,
)


@dataclass(frozen=True)
class EntryConfirmationResult:
    """
    Result returned by
    Entry Confirmation Engine.
    """

    confirmations: list[EntryConfirmation] = field(
        default_factory=list,
    )

    @property
    def confirmed_trades(
        self,
    ) -> list[EntryConfirmation]:
        """
        Return only confirmed trades.
        """

        return [
            confirmation
            for confirmation in self.confirmations
            if confirmation.confirmed
        ]
