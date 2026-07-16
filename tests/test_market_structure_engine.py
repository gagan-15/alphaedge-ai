"""
Market Structure Engine.

Sprint:
    2.31 - Market Structure Engine
"""

from pandas import DataFrame

from backend.config.bos_config import BOSConfig
from backend.core.logger import logger
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


class MarketStructureEngine:
    """
    Build canonical market structure.
    """

    def __init__(self) -> None:

        self._swing_detector = SwingDetector(
            BOSConfig(),
        )

    def analyze(
        self,
        market_data: DataFrame,
    ) -> MarketStructureResult:
        """
        Analyze market structure.
        """

        logger.info(
            "Analyzing market structure.",
        )

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

        logger.info(
            "%d structure point(s) detected.",
            len(structure_points),
        )

        return MarketStructureResult(
            state=state,
            structure_points=structure_points,
        )

    def _classify_structure_points(
        self,
        swings: list[SwingPoint],
    ) -> list[StructurePoint]:

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

        higher_high = self._latest_price(
            structure_points,
            StructurePointType.HIGHER_HIGH,
        )

        higher_low = self._latest_price(
            structure_points,
            StructurePointType.HIGHER_LOW,
        )

        lower_high = self._latest_price(
            structure_points,
            StructurePointType.LOWER_HIGH,
        )

        lower_low = self._latest_price(
            structure_points,
            StructurePointType.LOWER_LOW,
        )

        trend = StructureTrend.SIDEWAYS

        if (
            higher_high is not None
            and higher_low is not None
            and lower_high is None
            and lower_low is None
        ):
            trend = StructureTrend.BULLISH

        elif (
            lower_high is not None
            and lower_low is not None
            and higher_high is None
            and higher_low is None
        ):
            trend = StructureTrend.BEARISH

        return StructureState(
            trend=trend,
            last_higher_high=higher_high,
            last_higher_low=higher_low,
            last_lower_high=lower_high,
            last_lower_low=lower_low,
        )

    @staticmethod
    def _latest_price(
        structure_points: list[StructurePoint],
        point_type: StructurePointType,
    ) -> float | None:

        matching = [
            point for point in structure_points if point.point_type == point_type
        ]

        if not matching:
            return None

        return matching[-1].price
