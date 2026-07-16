"""
Market Structure Engine.

Sprint:
    2.30 - Market Structure Foundation
"""

from pandas import DataFrame

from backend.engines.demand_supply_engine.swing_detector import (
    SwingDetector,
)
from backend.models.market_structure.market_structure_point import (
    StructurePoint,
    StructurePointType,
)
from backend.models.market_structure.market_structure_result import (
    MarketStructureResult,
)
from backend.models.market_structure.market_structure_state import (
    StructureState,
    StructureTrend,
)
from backend.models.swing_point import (
    SwingPoint,
    SwingType,
)
from backend.validators.market_structure_validator import (
    MarketStructureValidator,
)
from backend.core.logger import logger


class MarketStructureEngine:
    """
    Build canonical market structure from confirmed swing points.
    """

    def __init__(self) -> None:
        self._swing_detector = SwingDetector()

    logger.info("Analyzing market structure.")

    def analyze(
        self,
        market_data: DataFrame,
    ) -> MarketStructureResult:
        """
        Analyze market structure.
        """

        MarketStructureValidator.validate_market_data(
            market_data,
        )

        swings = self._swing_detector.detect(
            market_data,
        )

        structure_points = self._classify_structure_points(
            swings,
        )

        state = self._resolve_structure_state(
            structure_points,
        )

        return MarketStructureResult(
            state=state,
            structure_points=structure_points,
        )

    def _classify_structure_points(
        self,
        swings: list[SwingPoint],
    ) -> list[StructurePoint]:
        """
        Classify swings as HH, HL, LH, LL, equal high or equal low.
        """

        structure_points: list[StructurePoint] = []

        previous_high: SwingPoint | None = None
        previous_low: SwingPoint | None = None

        for swing in swings:

            if swing.swing_type == SwingType.HIGH:

                point_type = self._classify_high(
                    swing,
                    previous_high,
                )

                structure_points.append(
                    StructurePoint(
                        swing=swing,
                        point_type=point_type,
                        previous_swing=previous_high,
                    )
                )

                previous_high = swing

            else:

                point_type = self._classify_low(
                    swing,
                    previous_low,
                )

                structure_points.append(
                    StructurePoint(
                        swing=swing,
                        point_type=point_type,
                        previous_swing=previous_low,
                    )
                )

                previous_low = swing

        return structure_points

    @staticmethod
    def _classify_high(
        swing: SwingPoint,
        previous_high: SwingPoint | None,
    ) -> StructurePointType:
        """
        Classify a swing high.
        """

        if previous_high is None:
            return StructurePointType.EQUAL_HIGH

        if swing.price > previous_high.price:
            return StructurePointType.HIGHER_HIGH

        if swing.price < previous_high.price:
            return StructurePointType.LOWER_HIGH

        return StructurePointType.EQUAL_HIGH

    @staticmethod
    def _classify_low(
        swing: SwingPoint,
        previous_low: SwingPoint | None,
    ) -> StructurePointType:
        """
        Classify a swing low.
        """

        if previous_low is None:
            return StructurePointType.EQUAL_LOW

        if swing.price > previous_low.price:
            return StructurePointType.HIGHER_LOW

        if swing.price < previous_low.price:
            return StructurePointType.LOWER_LOW

        return StructurePointType.EQUAL_LOW

    def _resolve_structure_state(
        self,
        structure_points: list[StructurePoint],
    ) -> StructureState:
        """
        Resolve the latest market structure trend and levels.
        """

        latest_higher_high = self._latest_price(
            structure_points,
            StructurePointType.HIGHER_HIGH,
        )

        latest_higher_low = self._latest_price(
            structure_points,
            StructurePointType.HIGHER_LOW,
        )

        latest_lower_high = self._latest_price(
            structure_points,
            StructurePointType.LOWER_HIGH,
        )

        latest_lower_low = self._latest_price(
            structure_points,
            StructurePointType.LOWER_LOW,
        )

        trend = StructureTrend.SIDEWAYS

        if (
            latest_higher_high is not None
            and latest_higher_low is not None
            and latest_lower_high is None
            and latest_lower_low is None
        ):
            trend = StructureTrend.BULLISH

        elif (
            latest_lower_high is not None
            and latest_lower_low is not None
            and latest_higher_high is None
            and latest_higher_low is None
        ):
            trend = StructureTrend.BEARISH

        else:
            trend = StructureTrend.SIDEWAYS

        return StructureState(
            trend=trend,
            last_higher_high=latest_higher_high,
            last_higher_low=latest_higher_low,
            last_lower_high=latest_lower_high,
            last_lower_low=latest_lower_low,
        )

    @staticmethod
    def _latest_price(
        structure_points: list[StructurePoint],
        point_type: StructurePointType,
    ) -> float | None:
        """
        Return the latest price for the requested structure point type.
        """

        matching_points = [
            point for point in structure_points if point.point_type == point_type
        ]

        if not matching_points:
            return None

        logger.info(
            "Detected %d structure point(s).",
            len(structure_points),
        )

        return matching_points[-1].swing.price
