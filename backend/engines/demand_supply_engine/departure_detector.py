"""Canonical Leg-Out and departure-strength detection."""

from __future__ import annotations

from pandas import DataFrame

from backend.engines.demand_supply_engine.candle_classifier import CandleClassifier
from backend.engines.demand_supply_engine.leg_detector import LegDetector
from backend.models.base_region import BaseRegion
from backend.models.candle_classification import CandleDirection
from backend.models.departure import (
    Departure,
    DepartureDirection,
    DepartureStrength,
)
from backend.models.price_leg import PriceLeg


class DepartureDetector:
    """Apply approved canonical Leg-In, Leg-Out and closing rules."""

    REQUIRED_COLUMNS = ("Open", "High", "Low", "Close")
    ATR_PERIOD = 14
    SIGNIFICANT_GAP_ATR_MULTIPLIER = 0.25

    def __init__(self, classifier: CandleClassifier | None = None) -> None:
        self._classifier = classifier or CandleClassifier()
        self._leg_detector = LegDetector(self._classifier)

    def detect(
        self, market_data: DataFrame, base: BaseRegion
    ) -> Departure | None:
        departure, _ = self._evaluate(market_data, base)
        return departure

    def diagnose(
        self, market_data: DataFrame, base: BaseRegion
    ) -> tuple[Departure | None, list[dict[str, object]]]:
        return self._evaluate(market_data, base)

    def _evaluate(
        self, market_data: DataFrame, base: BaseRegion
    ) -> tuple[Departure | None, list[dict[str, object]]]:
        self._validate_input(market_data, base)
        leg_in = self._leg_detector.detect_leg_in(market_data, base)
        leg_out = self._leg_detector.detect_leg_out(market_data, base)
        if leg_out is None:
            leg_out = self._gap_leg_out(market_data, base)
        rules: list[dict[str, object]] = [
            self._rule(
                "valid_leg_in",
                "Valid canonical Leg-In",
                leg_in is not None,
                0 if leg_in is None else leg_in.candle_count,
                "At least 1 aligned exciting candle",
            ),
            self._rule(
                "valid_leg_out",
                "Valid canonical Leg-Out",
                leg_out is not None,
                0 if leg_out is None else leg_out.candle_count,
                "Starts immediately with an exciting candle",
            ),
        ]
        if leg_in is None or leg_out is None:
            return None, rules

        base_data = market_data.iloc[base.start_index : base.end_index + 1]
        base_high = float(base_data["High"].max())
        base_low = float(base_data["Low"].min())
        first = market_data.iloc[leg_out.start_index]
        first_close = float(first["Close"])
        closes_outside_base = (
            first_close > base_high
            if leg_out.direction == DepartureDirection.BULLISH
            else first_close < base_low
        )
        good_closing = (
            first_close > leg_in.high
            if leg_out.direction == DepartureDirection.BULLISH
            else first_close < leg_in.low
        )
        significant_gap, gap_ratio = self._significant_gap(
            market_data, leg_out.start_index, leg_out.direction
        )
        leg_out_data = market_data.iloc[leg_out.start_index : leg_out.end_index + 1]
        no_close_back = bool(
            (leg_out_data["Close"] > base_high).all()
            if leg_out.direction == DepartureDirection.BULLISH
            else (leg_out_data["Close"] < base_low).all()
        )
        leg_in_data = market_data.iloc[leg_in.start_index : leg_in.end_index + 1]
        leg_out_data = market_data.iloc[leg_out.start_index : leg_out.end_index + 1]
        leg_in_move = abs(
            float(leg_in_data.iloc[-1]["Close"])
            - float(leg_in_data.iloc[0]["Open"])
        )
        previous_close = float(market_data.iloc[leg_out.start_index - 1]["Close"])
        leg_out_move = max(
            abs(
                float(leg_out_data.iloc[-1]["Close"])
                - float(leg_out_data.iloc[0]["Open"])
            ),
            abs(float(leg_out_data.iloc[-1]["Close"]) - previous_close),
        )
        stronger_than_leg_in = leg_out_move > leg_in_move

        strength: DepartureStrength | None = None
        if (
            good_closing
            and closes_outside_base
            and stronger_than_leg_in
            and leg_out.candle_count >= 2
            and significant_gap
            and no_close_back
        ):
            strength = DepartureStrength.VERY_STRONG
        elif (
            good_closing
            and closes_outside_base
            and stronger_than_leg_in
            and (leg_out.candle_count >= 2 or significant_gap)
        ):
            strength = DepartureStrength.STRONG
        elif (
            good_closing
            and closes_outside_base
            and stronger_than_leg_in
            and leg_out.candle_count == 1
            and not significant_gap
        ):
            strength = DepartureStrength.WEAK

        rules.extend(
            [
                self._rule(
                    "leg_out_vs_leg_in",
                    "Leg-Out stronger than complete Leg-In",
                    stronger_than_leg_in,
                    leg_out_move,
                    f"Greater than {leg_in_move}",
                ),
                self._rule(
                    "close_outside_base",
                    "First Leg-Out candle closes outside base",
                    closes_outside_base,
                    first_close,
                    f"Above {base_high} or below {base_low}",
                ),
                self._rule(
                    "good_closing",
                    "Closing Rule against complete Leg-In",
                    good_closing,
                    first_close,
                    f"Above {leg_in.high} or below {leg_in.low}",
                ),
                self._rule(
                    "significant_gap",
                    "Significant wick gap",
                    significant_gap,
                    gap_ratio,
                    f"At least {self.SIGNIFICANT_GAP_ATR_MULTIPLIER} ATR(14)",
                ),
                self._rule(
                    "departure_strength",
                    "Canonical departure strength",
                    strength is not None,
                    None if strength is None else strength.value,
                    "Weak, Strong or Very Strong",
                ),
            ]
        )
        if strength is None:
            return None, rules
        closing_reference = (
            leg_in.high
            if leg_out.direction == DepartureDirection.BULLISH
            else leg_in.low
        )
        acceptance_reason = (
            f"Accepted {strength.value.lower()} departure: canonical Leg-In and "
            "Leg-Out are valid, Leg-Out is stronger than Leg-In, and both "
            "closing rules passed."
        )
        return (
            Departure(
                direction=leg_out.direction,
                departure_index=leg_out.start_index,
                end_index=leg_out.end_index,
                strength=strength,
                leg_in_direction=leg_in.direction,
                leg_in_start_index=leg_in.start_index,
                leg_in_end_index=leg_in.end_index,
                significant_gap=significant_gap,
                good_closing=good_closing,
                gap_measurement=gap_ratio,
                closing_comparison_reference=closing_reference,
                qualifying_close=first_close,
                acceptance_reason=acceptance_reason,
            ),
            rules,
        )

    def _gap_leg_out(
        self, market_data: DataFrame, base: BaseRegion
    ) -> PriceLeg | None:
        index = base.end_index + 1
        if index >= len(market_data):
            return None
        previous = market_data.iloc[index - 1]
        current = market_data.iloc[index]
        if float(current["Low"]) > float(previous["High"]):
            direction = DepartureDirection.BULLISH
        elif float(current["High"]) < float(previous["Low"]):
            direction = DepartureDirection.BEARISH
        else:
            return None
        significant, _ = self._significant_gap(market_data, index, direction)
        classification = self._classifier.classify(market_data, index)
        expected = (
            CandleDirection.BULLISH
            if direction == DepartureDirection.BULLISH
            else CandleDirection.BEARISH
        )
        if not significant or classification.direction != expected:
            return None
        return PriceLeg(
            direction=direction,
            start_index=index,
            end_index=index,
            high=float(current["High"]),
            low=float(current["Low"]),
        )

    def _significant_gap(
        self,
        market_data: DataFrame,
        index: int,
        direction: DepartureDirection,
    ) -> tuple[bool, float | None]:
        if index <= 0:
            return False, None
        atr = self._atr_before(market_data, index)
        if atr is None or atr <= 0:
            return False, None
        previous = market_data.iloc[index - 1]
        current = market_data.iloc[index]
        if direction == DepartureDirection.BULLISH:
            gap = max(0.0, float(current["Low"]) - float(previous["High"]))
        else:
            gap = max(0.0, float(previous["Low"]) - float(current["High"]))
        ratio = gap / atr
        return ratio >= self.SIGNIFICANT_GAP_ATR_MULTIPLIER, ratio

    def _atr_before(self, market_data: DataFrame, index: int) -> float | None:
        if index < self.ATR_PERIOD:
            return None
        true_ranges: list[float] = []
        start = max(0, index - self.ATR_PERIOD)
        for candle_index in range(start, index):
            candle = market_data.iloc[candle_index]
            high = float(candle["High"])
            low = float(candle["Low"])
            if candle_index == 0:
                true_range = high - low
            else:
                previous_close = float(market_data.iloc[candle_index - 1]["Close"])
                true_range = max(
                    high - low,
                    abs(high - previous_close),
                    abs(low - previous_close),
                )
            true_ranges.append(true_range)
        return sum(true_ranges) / len(true_ranges)

    @staticmethod
    def _rule(
        key: str,
        label: str,
        passed: bool,
        actual: object,
        required: object,
    ) -> dict[str, object]:
        return {
            "key": key,
            "label": label,
            "passed": passed,
            "actual": actual,
            "required": required,
        }

    @classmethod
    def _validate_input(cls, market_data: DataFrame, base: BaseRegion) -> None:
        if not isinstance(market_data, DataFrame):
            raise TypeError("Market data must be a pandas DataFrame.")
        if not isinstance(base, BaseRegion):
            raise TypeError("base must be a BaseRegion.")
        if market_data.empty:
            raise ValueError("Market data cannot be empty.")
        missing = [
            column for column in cls.REQUIRED_COLUMNS if column not in market_data
        ]
        if missing:
            raise ValueError(
                "Market data is missing required columns: " + ", ".join(missing)
            )
        if base.start_index >= len(market_data) or base.end_index >= len(market_data):
            raise ValueError("Base index is outside market data.")
