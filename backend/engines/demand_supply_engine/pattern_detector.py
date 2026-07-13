"""
Pattern Detector for AlphaEdge AI.

Sprint:
    2.26 - Zone Detection Engine
"""

from backend.core.logger import logger
from backend.models.departure import (
    Departure,
    DepartureDirection,
)
from backend.models.pattern import (
    Pattern,
    PatternType,
)


class PatternDetector:
    """
    Detect Demand & Supply patterns.

    This detector classifies a zone using:

    - Leg In direction
    - Base
    - Departure direction
    """

    def detect(
        self,
        leg_in_bullish: bool,
        departure: Departure,
    ) -> Pattern:
        """
        Detect the Demand/Supply pattern.

        Args:
            leg_in_bullish:
                True if the candles entering the base
                were bullish.

            departure:
                Valid Departure object.

        Returns:
            Pattern
        """

        logger.info("Starting pattern detection.")

        if departure.direction == DepartureDirection.BULLISH:

            if leg_in_bullish:

                logger.info("Pattern detected: " "RALLY_BASE_RALLY.")

                return Pattern(PatternType.RALLY_BASE_RALLY)

            logger.info("Pattern detected: " "DROP_BASE_RALLY.")

            return Pattern(PatternType.DROP_BASE_RALLY)

        if leg_in_bullish:

            logger.info("Pattern detected: " "RALLY_BASE_DROP.")

            return Pattern(PatternType.RALLY_BASE_DROP)

        logger.info("Pattern detected: " "DROP_BASE_DROP.")

        return Pattern(PatternType.DROP_BASE_DROP)
