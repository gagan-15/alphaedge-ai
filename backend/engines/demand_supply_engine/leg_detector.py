"""Canonical Leg-In and Leg-Out detection."""

from pandas import DataFrame

from backend.engines.demand_supply_engine.candle_classifier import CandleClassifier
from backend.models.base_region import BaseRegion
from backend.models.candle_classification import CandleDirection, CandleStructure
from backend.models.departure import DepartureDirection
from backend.models.price_leg import PriceLeg


class LegDetector:
    """Detect maximal, contiguous, aligned exciting-candle legs."""

    def __init__(self, classifier: CandleClassifier | None = None) -> None:
        self._classifier = classifier or CandleClassifier()

    def detect_leg_in(
        self, market_data: DataFrame, base: BaseRegion
    ) -> PriceLeg | None:
        end_index = base.start_index - 1
        if end_index < 0:
            return None
        end = self._classifier.classify(market_data, end_index)
        direction = self._direction(end.direction)
        if end.structure != CandleStructure.EXCITING or direction is None:
            return None

        start_index = end_index
        while start_index > 0:
            previous = self._classifier.classify(market_data, start_index - 1)
            if (
                previous.structure != CandleStructure.EXCITING
                or self._direction(previous.direction) != direction
                or self._has_wick_gap(market_data, start_index - 1, start_index)
            ):
                break
            start_index -= 1
        return self._build_leg(market_data, direction, start_index, end_index)

    def detect_leg_out(
        self, market_data: DataFrame, base: BaseRegion
    ) -> PriceLeg | None:
        start_index = base.end_index + 1
        if start_index >= len(market_data):
            return None
        first = self._classifier.classify(market_data, start_index)
        direction = self._direction(first.direction)
        if first.structure != CandleStructure.EXCITING or direction is None:
            return None

        end_index = start_index
        while end_index + 1 < len(market_data):
            following = self._classifier.classify(market_data, end_index + 1)
            if (
                following.structure != CandleStructure.EXCITING
                or self._direction(following.direction) != direction
            ):
                break
            end_index += 1
        return self._build_leg(market_data, direction, start_index, end_index)

    @staticmethod
    def _direction(direction: CandleDirection) -> DepartureDirection | None:
        if direction == CandleDirection.BULLISH:
            return DepartureDirection.BULLISH
        if direction == CandleDirection.BEARISH:
            return DepartureDirection.BEARISH
        return None

    @staticmethod
    def _has_wick_gap(market_data: DataFrame, left: int, right: int) -> bool:
        left_candle = market_data.iloc[left]
        right_candle = market_data.iloc[right]
        return bool(
            float(right_candle["Low"]) > float(left_candle["High"])
            or float(right_candle["High"]) < float(left_candle["Low"])
        )

    @staticmethod
    def _build_leg(
        market_data: DataFrame,
        direction: DepartureDirection,
        start_index: int,
        end_index: int,
    ) -> PriceLeg:
        data = market_data.iloc[start_index : end_index + 1]
        return PriceLeg(
            direction=direction,
            start_index=start_index,
            end_index=end_index,
            high=float(data["High"].max()),
            low=float(data["Low"].min()),
        )
