"""
Trade Setup Result.

Sprint:
    2.36 - Trade Setup Engine
"""

from dataclasses import dataclass, field

from backend.models.trade_setup.trade_setup import (
    TradeSetup,
)


@dataclass(frozen=True)
class TradeSetupResult:
    """
    Result returned by
    Trade Setup Engine.
    """

    trade_setups: list[TradeSetup] = field(
        default_factory=list,
    )

    @property
    def best_setup(
        self,
    ) -> TradeSetup | None:
        """
        Return the highest priority
        trade setup.
        """

        if not self.trade_setups:
            return None

        return self.trade_setups[0]
