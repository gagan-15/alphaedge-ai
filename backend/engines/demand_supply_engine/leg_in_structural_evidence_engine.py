"""Bounded shadow analysis of the directional approach into a Base."""

from statistics import median

from pandas import DataFrame

from backend.engines.demand_supply_engine.candle_classifier import CandleClassifier
from backend.models.base_region import BaseRegion
from backend.models.candle_classification import CandleDirection, CandleStructure
from backend.models.departure import Departure, DepartureDirection
from backend.models.leg_in_structural_evidence import (
    CanonicalLegInStructuralEvidence,
    LegInFormationValidity,
    LegInStructuralState,
)


class LegInStructuralEvidenceEngine:
    """Measure broader approach structure without deciding zone validity."""

    RANGE_LOOKBACK = 20
    MAX_STRUCTURAL_CANDLES = 12
    MATERIAL_ZONE_OVERLAP = 0.25
    # Conservative V1 constants selected against the five frozen datasets.
    MAX_WEAK_DISPLACEMENT_ZONE_WIDTH_RATIO = 0.25
    MAX_EXTREMELY_POOR_DIRECTIONAL_EFFICIENCY = 0.10
    MIN_REPEATED_PRE_LEG_IN_OCCUPANCY = 0.90
    MIN_MEANINGFUL_BODY_OVERLAP = 0.50
    MIN_REPEATED_DIRECTION_CHANGES = 2
    MIN_EXTREME_PRE_BASE_OCCUPANCY = 1.0
    MIN_EXTREME_ADJACENT_BODY_OVERLAP = 1.0
    MIN_EXTREME_DIRECTION_CHANGES = 1
    MAX_EXTREME_CONGESTION_EFFICIENCY = 0.46
    MAX_EXTREME_CONGESTION_DISPLACEMENT_RATIO = 0.50

    def __init__(self, classifier: CandleClassifier | None = None) -> None:
        self._classifier = classifier or CandleClassifier()

    def evaluate(
        self,
        market_data: DataFrame,
        base: BaseRegion,
        departure: Departure,
        proximal: float,
        distal: float,
    ) -> CanonicalLegInStructuralEvidence:
        if departure.leg_in_start_index is None or departure.leg_in_end_index is None:
            raise ValueError("Canonical Leg-In indexes are required.")
        direction = departure.leg_in_direction
        if direction is None:
            raise ValueError("Canonical Leg-In direction is required.")

        start = departure.leg_in_start_index
        end = departure.leg_in_end_index
        expected = (
            CandleDirection.BEARISH
            if direction == DepartureDirection.BEARISH
            else CandleDirection.BULLISH
        )
        pauses = 0
        cursor = start - 1
        stop_reason = "START_OF_VALIDATED_SEGMENT"
        while cursor >= 0 and end - cursor < self.MAX_STRUCTURAL_CANDLES:
            classification = self._classifier.classify(market_data, cursor)
            if (
                classification.structure == CandleStructure.EXCITING
                and classification.direction != expected
            ):
                stop_reason = "OPPOSITE_EXCITING_IMPULSE"
                break
            if classification.structure in {
                CandleStructure.BASE,
                CandleStructure.BOUNDARY,
            }:
                if pauses >= 1:
                    stop_reason = "SECOND_PAUSE_OR_CONGESTION"
                    break
                pauses += 1
                start = cursor
                cursor -= 1
                continue
            if classification.direction == expected:
                start = cursor
                cursor -= 1
                continue
            stop_reason = "UNRELATED_OR_NEUTRAL_STRUCTURE"
            break
        else:
            if cursor >= 0:
                stop_reason = "MAXIMUM_STRUCTURAL_BOUNDARY"

        approach = market_data.iloc[start : end + 1]
        first_open = float(approach.iloc[0]["Open"])
        final_close = float(approach.iloc[-1]["Close"])
        displacement = max(
            0.0,
            (
                first_open - final_close
                if direction == DepartureDirection.BEARISH
                else final_close - first_open
            ),
        )
        points = [first_open, *map(float, approach["Close"])]
        travel = sum(abs(right - left) for left, right in zip(points, points[1:]))
        efficiency = displacement / max(travel, 1e-9)
        width = max(abs(proximal - distal), 1e-9)
        prior = market_data.iloc[max(0, start - self.RANGE_LOOKBACK) : start]
        ranges = [
            float(row.High - row.Low)
            for row in prior.itertuples()
            if float(row.High) > float(row.Low)
        ]
        normal_range = median(ranges) if ranges else None

        overlap_values = []
        body_overlap_values = []
        occupancy = 0
        direction_changes = 0
        previous_direction = None
        lower, upper = min(proximal, distal), max(proximal, distal)
        for position, row in enumerate(approach.itertuples()):
            classification = self._classifier.classify(market_data, start + position)
            if previous_direction is not None and classification.direction not in {
                previous_direction,
                CandleDirection.NEUTRAL,
            }:
                direction_changes += 1
            if classification.direction != CandleDirection.NEUTRAL:
                previous_direction = classification.direction
            candle_range = max(float(row.High - row.Low), 1e-9)
            zone_overlap = max(
                0.0, min(float(row.High), upper) - max(float(row.Low), lower)
            )
            occupancy += zone_overlap / candle_range >= self.MATERIAL_ZONE_OVERLAP
            if position:
                previous = approach.iloc[position - 1]
                overlap = max(
                    0.0,
                    min(float(previous["High"]), float(row.High))
                    - max(float(previous["Low"]), float(row.Low)),
                )
                overlap_values.append(
                    overlap
                    / max(
                        min(
                            float(previous["High"] - previous["Low"]),
                            candle_range,
                        ),
                        1e-9,
                    )
                )
                previous_body_low = min(
                    float(previous["Open"]), float(previous["Close"])
                )
                previous_body_high = max(
                    float(previous["Open"]), float(previous["Close"])
                )
                body_low = min(float(row.Open), float(row.Close))
                body_high = max(float(row.Open), float(row.Close))
                body_overlap = max(
                    0.0,
                    min(previous_body_high, body_high)
                    - max(previous_body_low, body_low),
                )
                body_overlap_values.append(
                    body_overlap
                    / max(
                        min(
                            previous_body_high - previous_body_low,
                            body_high - body_low,
                        ),
                        1e-9,
                    )
                )
        overlap_ratio = (
            sum(overlap_values) / len(overlap_values) if overlap_values else 0.0
        )
        occupancy_ratio = occupancy / len(approach)
        pre_leg_in_count = max(0, departure.leg_in_start_index - start)
        pre_leg_in_occupancy = (
            sum(
                1
                for row in approach.iloc[:pre_leg_in_count].itertuples()
                if max(
                    0.0,
                    min(float(row.High), upper) - max(float(row.Low), lower),
                )
                / max(float(row.High - row.Low), 1e-9)
                >= self.MATERIAL_ZONE_OVERLAP
            )
            / pre_leg_in_count
            if pre_leg_in_count
            else None
        )
        body_overlap_ratio = (
            sum(body_overlap_values) / len(body_overlap_values)
            if body_overlap_values
            else 0.0
        )
        width_ratio = displacement / width
        volatility_ratio = displacement / normal_range if normal_range else None
        state, reasons = self._classify(
            width_ratio,
            volatility_ratio,
            efficiency,
            overlap_ratio,
            occupancy_ratio,
            direction_changes,
        )
        validity, rejection_reasons = self._formation_validity(
            width_ratio=width_ratio,
            efficiency=efficiency,
            pre_leg_in_occupancy=pre_leg_in_occupancy,
            body_overlap=body_overlap_ratio,
            direction_changes=direction_changes,
            stop_reason=stop_reason,
        )
        return CanonicalLegInStructuralEvidence(
            broader_approach_start_index=start,
            broader_approach_end_index=end,
            approach_candle_count=len(approach),
            leg_in_candle_count=departure.leg_in_end_index
            - departure.leg_in_start_index
            + 1,
            leg_in_direction=direction,
            directional_displacement=round(displacement, 6),
            total_approach_travel=round(travel, 6),
            directional_efficiency=round(efficiency, 6),
            displacement_zone_width_ratio=round(width_ratio, 6),
            displacement_volatility_ratio=(
                round(volatility_ratio, 6) if volatility_ratio is not None else None
            ),
            approach_overlap_ratio=round(overlap_ratio, 6),
            prior_zone_occupancy_ratio=round(occupancy_ratio, 6),
            pre_leg_in_occupancy_ratio=(
                round(pre_leg_in_occupancy, 6)
                if pre_leg_in_occupancy is not None
                else None
            ),
            adjacent_body_overlap_ratio=round(body_overlap_ratio, 6),
            approach_direction_changes=direction_changes,
            pause_candle_count=pauses,
            backward_walk_stop_reason=stop_reason,
            structural_state=state,
            reason_codes=reasons,
            formation_validity=validity,
            formation_rejection_reasons=rejection_reasons,
        )

    @classmethod
    def _formation_validity(
        cls,
        *,
        width_ratio: float,
        efficiency: float,
        pre_leg_in_occupancy: float | None,
        body_overlap: float,
        direction_changes: int,
        stop_reason: str,
    ) -> tuple[LegInFormationValidity, tuple[str, ...]]:
        """Reject only when weak travel, prior occupancy and congestion agree."""
        weak_direction = (
            width_ratio <= cls.MAX_WEAK_DISPLACEMENT_ZONE_WIDTH_RATIO
            and efficiency <= cls.MAX_EXTREMELY_POOR_DIRECTIONAL_EFFICIENCY
        )
        repeated_occupancy = (
            pre_leg_in_occupancy is not None
            and pre_leg_in_occupancy >= cls.MIN_REPEATED_PRE_LEG_IN_OCCUPANCY
        )
        confirmations = []
        if body_overlap >= cls.MIN_MEANINGFUL_BODY_OVERLAP:
            confirmations.append("LEG_IN_MEANINGFUL_BODY_OVERLAP")
        if direction_changes >= cls.MIN_REPEATED_DIRECTION_CHANGES:
            confirmations.append("LEG_IN_REPEATED_DIRECTION_CHANGES")
        if stop_reason == "SECOND_PAUSE_OR_CONGESTION":
            confirmations.append("LEG_IN_CONGESTION_STOP")
        if efficiency <= 0.05:
            confirmations.append("LEG_IN_NEAR_ZERO_DIRECTIONAL_EFFICIENCY")

        if weak_direction and repeated_occupancy and confirmations:
            return (
                LegInFormationValidity.INVALID_CLEAR_CONGESTION,
                (
                    "LEG_IN_INSUFFICIENT_DIRECTIONAL_DISPLACEMENT",
                    "LEG_IN_REPEATED_PRE_BASE_ZONE_OCCUPANCY",
                    *confirmations,
                ),
            )
        extreme_pre_base_congestion = (
            pre_leg_in_occupancy is not None
            and pre_leg_in_occupancy >= cls.MIN_EXTREME_PRE_BASE_OCCUPANCY
            and body_overlap >= cls.MIN_EXTREME_ADJACENT_BODY_OVERLAP
            and stop_reason == "SECOND_PAUSE_OR_CONGESTION"
            and direction_changes >= cls.MIN_EXTREME_DIRECTION_CHANGES
            and efficiency <= cls.MAX_EXTREME_CONGESTION_EFFICIENCY
            and width_ratio <= cls.MAX_EXTREME_CONGESTION_DISPLACEMENT_RATIO
        )
        if extreme_pre_base_congestion:
            return (
                LegInFormationValidity.INVALID_CLEAR_CONGESTION,
                ("LEG_IN_EXTREME_PRE_BASE_CONGESTION",),
            )
        return LegInFormationValidity.VALID, ()

    @staticmethod
    def _classify(
        width_ratio: float,
        volatility_ratio: float | None,
        efficiency: float,
        overlap: float,
        occupancy: float,
        direction_changes: int,
    ) -> tuple[LegInStructuralState, tuple[str, ...]]:
        reasons = [
            (
                "LEG_IN_DISPLACEMENT_STRONG"
                if width_ratio >= 1
                else "LEG_IN_DISPLACEMENT_WEAK"
            ),
            "APPROACH_HIGH_OCCUPANCY" if occupancy > 0.8 else "APPROACH_LOW_OCCUPANCY",
            "APPROACH_HIGH_OVERLAP" if overlap > 0.8 else "APPROACH_OVERLAP_ACCEPTABLE",
            (
                "APPROACH_DIRECTIONAL"
                if efficiency >= 0.65 and direction_changes <= 1
                else "APPROACH_DIRECTION_CHANGES"
            ),
        ]
        if volatility_ratio is None:
            reasons.append("APPROACH_INSUFFICIENT_HISTORY")
            return LegInStructuralState.INSUFFICIENT_EVIDENCE, tuple(reasons)
        if occupancy > 0.8 and (width_ratio < 1.5 or overlap > 0.8):
            return LegInStructuralState.CONGESTED, tuple(reasons)
        if width_ratio >= 1 and occupancy <= 0.4 and efficiency >= 0.65:
            return LegInStructuralState.CLEAN, tuple(reasons)
        if width_ratio >= 0.5 and occupancy <= 0.65 and efficiency >= 0.5:
            return LegInStructuralState.ACCEPTABLE, tuple(reasons)
        return LegInStructuralState.BORDERLINE, tuple(reasons)
