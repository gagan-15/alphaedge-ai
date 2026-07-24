"""
Demand & Supply Engine.

Sprint:
    2.66 - Demand & Supply Detection
"""

from pandas import DataFrame

from backend.core.logger import logger
from backend.models.base_region import BaseRegion
from backend.models.departure import (
    Departure,
    DepartureDirection,
)
from backend.models.zone import (
    Zone,
    ZoneType,
)
from backend.services.zone_quality_service import (
    ZoneQualityService,
)
from backend.validators.zone_validator import (
    ZoneValidator,
)


class DemandSupplyEngine:
    """
    Detect Demand and Supply zones.
    """

    def validate(self, zone: Zone) -> Zone:
        """
        Validate a zone and return it unchanged.

        This method keeps the stable interface introduced by
        the Demand and Supply foundation.
        """

        logger.info("Starting zone validation.")

        ZoneValidator.validate_zone(zone)

        logger.info("Zone validation completed.")

        return zone

    @staticmethod
    def prepare_data(
        market_data: DataFrame,
    ) -> DataFrame:
        """
        Return an independent copy of market data.
        """

        logger.info(
            "Preparing market data for Demand/Supply analysis.",
        )

        return market_data.copy()

    def detect(
        self,
        market_data: DataFrame,
    ) -> list[Zone]:
        """
        Detect Demand and Supply zones.
        """

        logger.info(
            "Detecting Demand/Supply zones.",
        )

        zones: list[Zone] = []

        for index in range(
            2,
            len(market_data) - 2,
        ):

            base = self._detect_base(
                market_data,
                index,
            )

            if (
                base.candle_count
                > 2
            ):
                continue

            if not self._is_valid_base(
                market_data,
                base,
            ):
                continue

            departure = self._detect_departure(
                market_data,
                base,
            )

            if departure is None:
                continue

            if not self._has_valid_leg_in(
                market_data,
                base,
            ):
                continue

            candle = market_data.iloc[index]
            departure_candles = market_data.iloc[
                departure.departure_index :
                min(
                    departure.departure_index + 3,
                    len(market_data),
                )
            ]

            next_candle = departure_candles.iloc[0]

            if not self._has_valid_leg_out(
                candle,
                next_candle,
            ):
                continue

            touches = self._count_touches(
                market_data,
                candle["High"],
                candle["Low"],
                departure.departure_index,
            )

            if touches > 0:
                continue

            is_fresh = self._is_fresh_zone(
                market_data,
                departure.departure_index,
            )

            if not is_fresh:
                continue

            quality = ZoneQualityService.calculate(
                base_score=self._base_score(
                    market_data,
                    base,
                ),
                leg_in_score=self._leg_in_score(
                    market_data,
                    base,
                ),
                leg_out_score=100.0,
                freshness_score=100.0,
            )

            zones.append(
                Zone(
                    zone_type=(
                        ZoneType.DEMAND
                        if departure.direction
                        == DepartureDirection.BULLISH
                        else ZoneType.SUPPLY
                    ),
                    upper_price=float(
                        candle["High"],
                    ),
                    lower_price=float(
                        candle["Low"],
                    ),
                    created_index=index,

                    strength=quality.total_score,

                    is_fresh=is_fresh,
                    touch_count=touches,
                    merged_count=1,
                )
            )

        logger.info(
            "%d zone(s) detected.",
            len(zones),
        )

        return zones

    def _detect_base(
        self,
        market_data: DataFrame,
        index: int,
    ) -> BaseRegion:
        """
        Detect a 1-2 candle base.
        """

        if (
            index + 1 < len(market_data)
            and abs(
                market_data.iloc[index + 1]["Close"]
                - market_data.iloc[index + 1]["Open"]
            )
            <= abs(
                market_data.iloc[index]["Close"]
                - market_data.iloc[index]["Open"]
            )
        ):
            return BaseRegion(
                start_index=index,
                end_index=index + 1,
            )

        return BaseRegion(
            start_index=index,
            end_index=index,
        )

    @staticmethod
    def _detect_departure(
        market_data: DataFrame,
        region: BaseRegion,
    ) -> Departure | None:
        """
        Detect a strong bullish/bearish departure.
        """

        current = market_data.iloc[
            region.end_index
        ]

        next_candle = market_data.iloc[
            region.end_index + 1
        ]

        current_body = abs(
            float(current["Close"])
            - float(current["Open"])
        )

        departure_body = abs(
            float(next_candle["Close"])
            - float(next_candle["Open"])
        )

        if departure_body < current_body * 1.5:
            return None

        if (
            next_candle["Close"]
            > current["High"]
        ):
            return Departure(
                direction=DepartureDirection.BULLISH,
                departure_index=region.end_index + 1,
            )

        if (
            next_candle["Close"]
            < current["Low"]
        ):
            return Departure(
                direction=DepartureDirection.BEARISH,
                departure_index=region.end_index + 1,
            )

        return None

    @staticmethod
    def _is_fresh_zone(
        market_data: DataFrame,
        departure_index: int,
    ) -> bool:
        """
        Return True if the zone has not been retested.
        """

        departure_close = float(
            market_data.iloc[
                departure_index
            ]["Close"]
        )

        for index in range(
            departure_index + 1,
            len(market_data),
        ):

            candle = market_data.iloc[index]

            if (
                candle["Low"]
                <= departure_close
                <= candle["High"]
            ):
                return False

        return True

    @staticmethod
    def _calculate_strength(
        base_candle,
        departure_candles: DataFrame,
    ) -> float:
        """
        Calculate zone strength using the first
        three departure candles.
        """

        departure_move = (
            float(
                departure_candles["Close"].iloc[-1]
            )
            - float(base_candle["Close"])
        )

        departure_move = abs(
            departure_move,
        )

        base_range = (
            float(base_candle["High"])
            - float(base_candle["Low"])
        )

        if base_range == 0:
            return 0.0

        return round(
            departure_move / base_range,
            2,
        )

    @staticmethod
    def _count_touches(
        market_data: DataFrame,
        upper: float,
        lower: float,
        start_index: int,
    ) -> int:
        """
        Count how many times price revisited the zone.
        """

        touches = 0

        for index in range(
            start_index + 1,
            len(market_data),
        ):
            candle = market_data.iloc[index]

            if (
                candle["High"] >= lower
                and candle["Low"] <= upper
            ):
                touches += 1

        return touches

    @staticmethod
    def _is_valid_base(
        market_data: DataFrame,
        base: BaseRegion,
    ) -> bool:
        """
        Validate base candle quality.
        """

        for index in range(
            base.start_index,
            base.end_index + 1,
        ):

            candle = market_data.iloc[index]

            body = abs(
                float(candle["Close"])
                - float(candle["Open"])
            )

            range_size = (
                float(candle["High"])
                - float(candle["Low"])
            )

            if range_size == 0:
                return False

            body_percent = (
                body / range_size
            ) * 100

            if body_percent > 50:
                return False

        return True

    @staticmethod
    def _has_valid_leg_in(
        market_data: DataFrame,
        base: BaseRegion,
    ) -> bool:
        """
        Validate the leg-in before the base.
        """

        if base.start_index == 0:
            return False

        previous = market_data.iloc[
            base.start_index - 1
        ]

        base_candle = market_data.iloc[
            base.start_index
        ]

        previous_body = abs(
            float(previous["Close"])
            - float(previous["Open"])
        )

        base_body = abs(
            float(base_candle["Close"])
            - float(base_candle["Open"])
        )

        return previous_body > base_body

    @staticmethod
    def _has_valid_leg_out(
        base_candle,
        departure_candle,
    ) -> bool:
        """
        Validate the departure candle.
        """

        base_body = abs(
            float(base_candle["Close"])
            - float(base_candle["Open"])
        )

        departure_body = abs(
            float(departure_candle["Close"])
            - float(departure_candle["Open"])
        )

        departure_range = (
            float(departure_candle["High"])
            - float(departure_candle["Low"])
        )

        if departure_range == 0:
            return False

        body_percent = (
            departure_body
            / departure_range
        ) * 100

        return (
            departure_body >= base_body * 2
            and body_percent >= 70
        )

    @staticmethod
    def _base_score(
        market_data: DataFrame,
        base: BaseRegion,
    ) -> float:
        """
        Calculate base quality score.
        """

        score = 100.0

        for index in range(
            base.start_index,
            base.end_index + 1,
        ):

            candle = market_data.iloc[index]

            body = abs(
                float(candle["Close"])
                - float(candle["Open"])
            )

            candle_range = (
                float(candle["High"])
                - float(candle["Low"])
            )

            if candle_range == 0:
                return 0.0

            body_percent = (
                body / candle_range
            ) * 100

            score -= max(
                0,
                body_percent - 30,
            )

        return max(
            0.0,
            round(score, 2),
        )

    @staticmethod
    def _leg_in_score(
        market_data: DataFrame,
        base: BaseRegion,
    ) -> float:
        """
        Calculate the strength of the leg-in.
        """

        if base.start_index == 0:
            return 0.0

        previous = market_data.iloc[
            base.start_index - 1
        ]

        base_candle = market_data.iloc[
            base.start_index
        ]

        previous_body = abs(
            float(previous["Close"])
            - float(previous["Open"])
        )

        base_body = abs(
            float(base_candle["Close"])
            - float(base_candle["Open"])
        )

        if base_body == 0:
            return 100.0

        score = min(
            100.0,
            (previous_body / base_body) * 50,
        )

        return round(
            score,
            2,
        )
