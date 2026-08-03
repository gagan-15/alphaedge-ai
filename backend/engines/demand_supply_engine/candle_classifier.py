"""Canonical candle classification for the zone-formation engine."""

from __future__ import annotations

from decimal import Decimal
from statistics import median

from pandas import DataFrame

from backend.models.candle_classification import (
    CandleClassification,
    CandleDirection,
    CandleStructure,
)


class CandleClassifier:
    """Classify validated OHLC candles using approved deterministic rules."""

    EXPLOSIVE_BODY_RATIO = Decimal("0.70")
    EXPLOSIVE_RANGE_MULTIPLIER = 1.5
    EXPLOSIVE_CLOSE_FRACTION = 0.20
    RANGE_LOOKBACK = 20

    def classify(self, market_data: DataFrame, index: int) -> CandleClassification:
        candle = market_data.iloc[index]
        open_price = Decimal(str(candle["Open"]))
        high_price = Decimal(str(candle["High"]))
        low_price = Decimal(str(candle["Low"]))
        close_price = Decimal(str(candle["Close"]))
        candle_range = high_price - low_price
        if candle_range <= 0:
            raise ValueError("Canonical classification requires a positive range.")

        body = abs(close_price - open_price)
        body_ratio = body / candle_range
        if body_ratio < Decimal("0.50"):
            structure = CandleStructure.BASE
        elif body_ratio > Decimal("0.50"):
            structure = CandleStructure.EXCITING
        else:
            structure = CandleStructure.BOUNDARY

        if close_price > open_price:
            direction = CandleDirection.BULLISH
            close_location = float((high_price - close_price) / candle_range)
        elif close_price < open_price:
            direction = CandleDirection.BEARISH
            close_location = float((close_price - low_price) / candle_range)
        else:
            direction = CandleDirection.NEUTRAL
            close_location = None

        prior_ranges = self._prior_ranges(market_data, index)
        range_to_median = None
        explosive = False
        if len(prior_ranges) == self.RANGE_LOOKBACK:
            median_range = median(prior_ranges)
            if median_range > 0:
                range_to_median = float(candle_range) / median_range
                explosive = (
                    structure == CandleStructure.EXCITING
                    and body_ratio >= self.EXPLOSIVE_BODY_RATIO
                    and range_to_median >= self.EXPLOSIVE_RANGE_MULTIPLIER
                    and close_location is not None
                    and close_location <= self.EXPLOSIVE_CLOSE_FRACTION
                )

        return CandleClassification(
            index=index,
            direction=direction,
            structure=structure,
            body=float(body),
            candle_range=float(candle_range),
            body_ratio=float(body_ratio),
            explosive=explosive,
            range_to_median=range_to_median,
            close_location=close_location,
        )

    def classify_all(self, market_data: DataFrame) -> list[CandleClassification]:
        return [self.classify(market_data, index) for index in range(len(market_data))]

    def _prior_ranges(self, market_data: DataFrame, index: int) -> list[float]:
        start = max(0, index - self.RANGE_LOOKBACK)
        ranges: list[float] = []
        for prior_index in range(start, index):
            candle = market_data.iloc[prior_index]
            candle_range = float(candle["High"]) - float(candle["Low"])
            if candle_range > 0:
                ranges.append(candle_range)
        return ranges
