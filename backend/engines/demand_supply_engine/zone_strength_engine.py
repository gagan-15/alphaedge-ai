"""
Zone Strength Engine.

Sprint:
    2.28 - Zone Strength Engine
"""

from pandas import DataFrame

from backend.core.logger import logger
from backend.models.zone import Zone, ZoneType
from backend.models.zone_strength_result import (
    StrengthStatus,
    ZoneStrengthResult,
)
from backend.validators.zone_strength_validator import (
    ZoneStrengthValidator,
)
from backend.config.zone_strength_config import (
    ZoneStrengthConfig,
)


class ZoneStrengthEngine:
    """
    Evaluate the strength of a detected zone.
    """

    def evaluate(
        self,
        zone: Zone,
        market_data: DataFrame,
    ) -> ZoneStrengthResult:
        """
        Evaluate zone strength.
        """

        logger.info("Starting zone strength evaluation.")

        ZoneStrengthValidator.validate(
            zone,
            market_data,
        )

        departure_distance = self._calculate_departure_distance(
            zone,
            market_data,
        )

        departure_candle_count = self._count_departure_candles(
            zone,
            market_data,
        )

        departure_speed = (
            departure_distance / departure_candle_count
            if departure_candle_count > 0
            else 0.0
        )

        volume_confirmed = self._volume_confirmed(
            market_data,
        )

        gap_present = self._gap_present(
            zone,
            market_data,
        )

        status = self._determine_strength_status(
            departure_distance,
        )

        result = ZoneStrengthResult(
            status=status,
            departure_distance=departure_distance,
            departure_candle_count=departure_candle_count,
            departure_speed=departure_speed,
            volume_confirmed=volume_confirmed,
            gap_present=gap_present,
        )

        logger.info("Zone strength evaluation completed.")

        return result

    def _calculate_departure_distance(
        self,
        zone: Zone,
        market_data: DataFrame,
    ) -> float:
        """
        Calculate how far price moved away
        from the zone.
        """

        future_data = market_data.iloc[zone.created_index + 1 :]

        if future_data.empty:
            return 0.0

        zone_height = zone.upper_price - zone.lower_price

        if zone_height <= 0:
            return 0.0

        if zone.zone_type == ZoneType.DEMAND:

            highest_price = float(future_data["High"].max())

            departure = highest_price - zone.upper_price

        else:

            lowest_price = float(future_data["Low"].min())

            departure = zone.lower_price - lowest_price

        return max(
            departure / zone_height,
            0.0,
        )

    def _count_departure_candles(
        self,
        zone: Zone,
        market_data: DataFrame,
    ) -> int:
        """
        Count consecutive candles moving away
        from the zone.
        """

        future_data = market_data.iloc[zone.created_index + 1 :]

        count = 0

        for _, candle in future_data.iterrows():

            open_price = float(candle["Open"])
            close_price = float(candle["Close"])

            if zone.zone_type == ZoneType.DEMAND:

                if close_price > open_price:
                    count += 1
                else:
                    break

            else:

                if close_price < open_price:
                    count += 1
                else:
                    break

        return count

    def _calculate_departure_speed(
        self,
        zone: Zone,
        market_data: DataFrame,
    ) -> float:
        """
        Calculate departure speed as the
        departure distance per departure candle.
        """

        departure_distance = self._calculate_departure_distance(
            zone,
            market_data,
        )

        departure_candles = self._count_departure_candles(
            zone,
            market_data,
        )

        if departure_candles == 0:
            return 0.0

        return departure_distance / departure_candles

    def _determine_strength_status(
        self,
        departure_distance: float,
    ) -> StrengthStatus:
        """
        Determine the overall strength
        of the zone.
        """
        if departure_distance >= ZoneStrengthConfig.VERY_STRONG_DEPARTURE:
            return StrengthStatus.VERY_STRONG

        if departure_distance >= ZoneStrengthConfig.STRONG_DEPARTURE:
            return StrengthStatus.STRONG

        if departure_distance >= ZoneStrengthConfig.MODERATE_DEPARTURE:
            return StrengthStatus.MODERATE

        return StrengthStatus.WEAK

    def _volume_confirmed(
        self,
        market_data: DataFrame,
    ) -> bool:
        """
        Determine whether the latest candle
        has above-average volume.
        """

        if "Volume" not in market_data.columns:
            return False

        if len(market_data) < 2:
            return False

        average_volume = float(market_data["Volume"].mean())

        latest_volume = float(market_data.iloc[-1]["Volume"])

        return latest_volume > average_volume

    def _gap_present(
        self,
        zone: Zone,
        market_data: DataFrame,
    ) -> bool:
        """
        Determine whether an opening gap
        occurred immediately after the zone.
        """

        future_data = market_data.iloc[zone.created_index + 1 :]

        if future_data.empty:
            return False

        first = future_data.iloc[0]

        open_price = float(first["Open"])

        if zone.zone_type == ZoneType.DEMAND:

            return open_price > zone.upper_price

        return open_price < zone.lower_price
