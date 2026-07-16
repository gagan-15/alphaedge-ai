"""
Trade Setup Engine.

Sprint:
    2.36 - Trade Setup Engine
"""

from backend.config.trade_setup_config import (
    TradeSetupConfig,
)
from backend.models.trade_setup.trade_setup import (
    TradeSetup,
)
from backend.models.trade_setup.trade_setup_result import (
    TradeSetupResult,
)
from backend.models.zone import ZoneType
from backend.models.zone_ranking.zone_rank import (
    ZoneRank,
)
from backend.validators.trade_setup_validator import (
    TradeSetupValidator,
)


class TradeSetupEngine:
    """
    Generate trade setups from ranked zones.
    """

    def __init__(
        self,
        config: TradeSetupConfig | None = None,
    ) -> None:

        self._config = config or TradeSetupConfig()

    def generate(
        self,
        ranked_zones: list[ZoneRank],
    ) -> TradeSetupResult:
        """
        Generate trade setups.
        """

        TradeSetupValidator.validate(
            ranked_zones,
            self._config,
        )

        setups: list[TradeSetup] = []

        for ranked_zone in ranked_zones:

            zone = ranked_zone.zone_score.zone

            entry = (
                zone.lower_price
                if zone.zone_type == ZoneType.DEMAND
                else zone.upper_price
            )

            stop = (
                zone.lower_price * (1 - self._config.stop_buffer_percentage / 100)
                if zone.zone_type == ZoneType.DEMAND
                else zone.upper_price * (1 + self._config.stop_buffer_percentage / 100)
            )

            risk = abs(entry - stop)

            target = (
                entry + (risk * self._config.minimum_risk_reward)
                if zone.zone_type == ZoneType.DEMAND
                else entry - (risk * self._config.minimum_risk_reward)
            )

            setups.append(
                TradeSetup(
                    zone=zone,
                    entry_price=entry,
                    stop_loss=stop,
                    target_price=target,
                    risk_reward_ratio=self._config.minimum_risk_reward,
                    is_buy=(zone.zone_type == ZoneType.DEMAND),
                )
            )

        return TradeSetupResult(
            trade_setups=setups,
        )
