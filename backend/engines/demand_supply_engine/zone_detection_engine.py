"""
Zone Detection Engine for AlphaEdge AI.

Sprint:
    2.26 - Zone Detection Engine
"""

from pandas import DataFrame

from backend.core.logger import logger
from backend.engines.demand_supply_engine.base_detector import (
    BaseDetector,
)
from backend.engines.demand_supply_engine.departure_detector import (
    DepartureDetector,
)
from backend.engines.demand_supply_engine.pattern_detector import (
    PatternDetector,
)
from backend.models.zone import (
    Zone,
    ZoneType,
)
from backend.validators.zone_validator import (
    ZoneValidator,
)


class ZoneDetectionEngine:
    """
    Detect Demand and Supply zones.

    This class orchestrates the complete
    zone detection workflow.

    Responsibilities

    1. Detect Bases
    2. Detect Departures
    3. Detect Patterns
    4. Create Zones
    5. Validate Zones
    """

    def __init__(self) -> None:

        self._base_detector = BaseDetector()

        self._departure_detector = DepartureDetector()

        self._pattern_detector = PatternDetector()

    def detect_zones(
        self,
        market_data: DataFrame,
    ) -> list[Zone]:
        """
        Detect all valid demand
        and supply zones.
        """

        logger.info("Starting zone detection.")

        detected_zones: list[Zone] = []

        base_regions = self._base_detector.detect(market_data)

        logger.info(f"{len(base_regions)} base region(s) detected.")

        for base in base_regions:

            departure = self._departure_detector.detect(
                market_data,
                base,
            )

            if departure is None:

                logger.info("Skipping base because " "no valid departure exists.")

                continue

            leg_in_bullish = self._is_leg_in_bullish(
                market_data,
                base.start_index,
            )

            pattern = self._pattern_detector.detect(
                leg_in_bullish,
                departure,
            )

            zone = self._create_zone(
                market_data,
                base,
                pattern,
            )

            ZoneValidator.validate_zone(zone)

            detected_zones.append(zone)

        logger.info(
            "Zone detection completed. " f"{len(detected_zones)} zone(s) detected."
        )

        return detected_zones

    def _create_zone(
        self,
        market_data: DataFrame,
        base,
        pattern,
    ) -> Zone:
        """
        Create a Zone object from
        a detected BaseRegion.
        """

        base_data = market_data.iloc[base.start_index : base.end_index + 1]

        upper_price = float(base_data["High"].max())

        lower_price = float(base_data["Low"].min())

        if pattern.pattern_type.value in (
            "DROP_BASE_RALLY",
            "RALLY_BASE_RALLY",
        ):
            zone_type = ZoneType.DEMAND
        else:
            zone_type = ZoneType.SUPPLY

        logger.info(
            "Creating %s zone.",
            zone_type.value,
        )

        return Zone(
            zone_type=zone_type,
            upper_price=upper_price,
            lower_price=lower_price,
            created_index=base.end_index,
        )

    @staticmethod
    def _is_leg_in_bullish(
        market_data: DataFrame,
        base_start_index: int,
    ) -> bool:
        """
        Determine the direction of the
        candle immediately before the base.

        Returns:
            True:
                Bullish leg-in.

            False:
                Bearish leg-in.
        """

        if base_start_index == 0:
            return False

        previous_candle = market_data.iloc[base_start_index - 1]

        return float(previous_candle["Close"]) > float(previous_candle["Open"])
