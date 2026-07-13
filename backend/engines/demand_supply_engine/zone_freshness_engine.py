"""
Zone Freshness Engine for AlphaEdge AI.

Sprint:
    2.27 - Zone Freshness Engine
"""

from pandas import DataFrame

from backend.core.logger import logger
from backend.models.zone import Zone, ZoneType
from backend.models.zone_freshness_result import (
    FreshnessStatus,
    ZoneFreshnessResult,
)
from backend.validators.zone_freshness_validator import (
    ZoneFreshnessValidator,
)
from backend.config.zone_freshness_config import (
    ZoneFreshnessConfig,
)


class ZoneFreshnessEngine:
    """
    Evaluate the freshness of a detected zone.
    """

    def evaluate(
        self,
        zone: Zone,
        market_data: DataFrame,
    ) -> ZoneFreshnessResult:
        """
        Evaluate zone freshness.
        """

        logger.info("Starting zone freshness evaluation.")

        ZoneFreshnessValidator.validate(
            zone,
            market_data,
        )

        touch_count = self._count_touches(
            zone,
            market_data,
        )

        penetration = self._calculate_penetration(
            zone,
            market_data,
        )

        status = self._determine_status(
            touch_count,
            penetration,
        )

        result = ZoneFreshnessResult(
            status=status,
            touch_count=touch_count,
            penetration_percent=penetration,
            is_broken=(status == FreshnessStatus.BROKEN),
        )

        logger.info("Zone freshness evaluation completed.")

        return result

    def _count_touches(
        self,
        zone: Zone,
        market_data: DataFrame,
    ) -> int:
        """
        Count the number of times price
        re-enters the zone.
        """

        touch_count = 0
        inside_zone = False

        future_data = market_data.iloc[zone.created_index + 1 :]

        for _, candle in future_data.iterrows():

            high = float(candle["High"])
            low = float(candle["Low"])

            touches_zone = low <= zone.upper_price and high >= zone.lower_price

            if touches_zone and not inside_zone:
                touch_count += 1
                inside_zone = True

            elif not touches_zone:
                inside_zone = False

        return touch_count

    def _calculate_penetration(
        self,
        zone: Zone,
        market_data: DataFrame,
    ) -> float:
        """
        Calculate the maximum penetration
        into the zone.
        """

        max_penetration = 0.0

        future_data = market_data.iloc[zone.created_index + 1 :]

        zone_height = zone.upper_price - zone.lower_price

        if zone_height <= 0:
            return 0.0

        for _, candle in future_data.iterrows():

            low = float(candle["Low"])
            high = float(candle["High"])

            touches_zone = low <= zone.upper_price and high >= zone.lower_price

            if not touches_zone:
                continue

            if zone.zone_type == ZoneType.DEMAND:

                penetration = zone.upper_price - max(
                    low,
                    zone.lower_price,
                )

            else:
                penetration = (
                    min(
                        high,
                        zone.upper_price,
                    )
                    - zone.lower_price
                )

            if penetration > 0:

                penetration_percent = (penetration / zone_height) * 100

                max_penetration = max(
                    max_penetration,
                    min(penetration_percent, 100.0),
                )

        return max_penetration

    def _determine_status(
        self,
        touch_count: int,
        penetration_percent: float,
    ) -> FreshnessStatus:
        """
        Determine the freshness status.
        """

        if touch_count == 0:
            return FreshnessStatus.FRESH

        if penetration_percent >= ZoneFreshnessConfig.BROKEN_PENETRATION_PERCENT:
            return FreshnessStatus.BROKEN

        if penetration_percent >= ZoneFreshnessConfig.WEAK_PENETRATION_PERCENT:
            return FreshnessStatus.WEAK

        return FreshnessStatus.TESTED
