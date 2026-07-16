"""
Trade Setup Validator.

Sprint:
    2.36 - Trade Setup Engine
"""

from backend.config.trade_setup_config import (
    TradeSetupConfig,
)
from backend.models.zone_ranking.zone_rank import (
    ZoneRank,
)


class TradeSetupValidator:
    """
    Validate Trade Setup inputs.
    """

    @staticmethod
    def validate(
        ranked_zones: list[ZoneRank],
        config: TradeSetupConfig,
    ) -> None:

        if not ranked_zones:
            raise ValueError("ranked_zones cannot be empty.")

        if config.minimum_risk_reward <= 0:
            raise ValueError("minimum_risk_reward must be greater than zero.")

        if config.entry_buffer_percentage < 0:
            raise ValueError("entry_buffer_percentage cannot be negative.")

        if config.stop_buffer_percentage < 0:
            raise ValueError("stop_buffer_percentage cannot be negative.")
