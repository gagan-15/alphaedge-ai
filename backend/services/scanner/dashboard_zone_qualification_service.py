"""Strict, read-only formation gate for primary Dashboard candidates."""

from __future__ import annotations

from dataclasses import dataclass

from backend.config.timeframe_hierarchy import is_timeframe_at_or_below
from backend.models.candle_classification import (
    CandleDirection,
    CandleStructure,
)
from backend.models.departure import DepartureDirection
from backend.models.zone import Zone, ZoneType


@dataclass(frozen=True)
class DashboardZoneQualification:
    dashboard_qualified: bool
    qualification_reason_codes: tuple[str, ...]
    departure_quality: str
    base_quality: str
    formation_quality: str
    departure_displacement: float
    departure_zone_width_ratio: float
    explosive_candle_count: int
    aligned_exciting_candle_count: int
    leg_out_body_ratio: float
    leg_out_range_to_median: float | None
    directional_close_distance: float | None
    leg_out_to_leg_in_body_ratio: float
    base_candle_count: int
    base_compactness: str
    base_compactness_reason: str
    base_preference_rank: int


class DashboardZoneQualificationService:
    """Qualify accepted zones without changing canonical acceptance or scores."""

    MAX_BASE_CANDLES = 3
    EXPLOSIVE_MIN_BODY_TO_ZONE = 1.0
    EXPLOSIVE_MIN_CLEARANCE_TO_ZONE = 0.25
    MULTI_MIN_BODY_TO_ZONE = 1.5
    MULTI_MIN_CLEARANCE_TO_ZONE = 0.5
    MAX_EXPLOSIVE_CLOSE_DISTANCE = 0.25
    MAX_MULTI_CLOSE_DISTANCE = 0.35
    MIN_MULTI_RANGE_TO_MEDIAN = 1.0
    # A non-explosive single candle must pass every threshold below. Together
    # they measure body dominance, unusual range, directional closing quality,
    # separation from the base, and strength relative to the incoming leg.
    SINGLE_MIN_BODY_RATIO = 0.60
    SINGLE_MIN_RANGE_TO_MEDIAN = 1.50
    SINGLE_MAX_CLOSE_DISTANCE = 0.40
    SINGLE_MIN_CLEARANCE_TO_ZONE = 1.00
    SINGLE_MIN_BODY_TO_LEG_IN = 1.25

    def qualify(
        self,
        zone: Zone,
        timeframe: str | None = None,
    ) -> DashboardZoneQualification:
        evidence = zone.formation_evidence
        if evidence is None:
            return self._rejected("MALFORMED_OR_INCOMPLETE_EVIDENCE")

        reasons = [
            f"BASE_{evidence.base_candle_count}_CANDLE"
            + ("S" if evidence.base_candle_count != 1 else ""),
            "GAP_PRESENT" if evidence.significant_gap else "NO_GAP",
        ]
        valid_pattern = evidence.pattern in {"DBR", "RBR", "RBD", "DBD"}
        expected_structure = {
            "DBR": (ZoneType.DEMAND, DepartureDirection.BEARISH),
            "RBR": (ZoneType.DEMAND, DepartureDirection.BULLISH),
            "RBD": (ZoneType.SUPPLY, DepartureDirection.BULLISH),
            "DBD": (ZoneType.SUPPLY, DepartureDirection.BEARISH),
        }
        structure_matches = expected_structure.get(evidence.pattern) == (
            zone.zone_type,
            evidence.leg_in_direction,
        )
        complete = bool(
            evidence.leg_in_candles
            and evidence.base_candles
            and evidence.leg_out_candles
        )
        if not valid_pattern or not complete or not structure_matches:
            reasons.append("MALFORMED_OR_INCOMPLETE_EVIDENCE")
            return self._result(False, reasons, "MALFORMED", "MALFORMED", 0, 0, 0, 0)

        if evidence.base_candle_count > self.MAX_BASE_CANDLES:
            reasons.append("BASE_TOO_LONG_FOR_PRIMARY_DASHBOARD")
            return self._result(
                False,
                reasons,
                "NOT_EVALUATED",
                "NOT_PRIMARY",
                0,
                0,
                0,
                0,
                base_count=evidence.base_candle_count,
            )
        if (
            is_timeframe_at_or_below(timeframe, "1W")
            and evidence.base_candle_count > 1
        ):
            reasons.append("MULTI_BASE_EXECUTION_ZONE")
            return self._result(
                False,
                reasons,
                "NOT_EVALUATED",
                "NOT_PRIMARY",
                0,
                0,
                0,
                0,
                base_count=evidence.base_candle_count,
            )
        if any(
            candle.classification.structure != CandleStructure.BASE
            for candle in evidence.base_candles
        ):
            reasons.append("MALFORMED_OR_INCOMPLETE_EVIDENCE")
            return self._result(False, reasons, "MALFORMED", "INVALID", 0, 0, 0, 0)

        expected_direction = (
            CandleDirection.BULLISH
            if zone.zone_type == ZoneType.DEMAND
            else CandleDirection.BEARISH
        )
        aligned_exciting = tuple(
            candle.classification
            for candle in evidence.leg_out_candles
            if candle.classification.structure == CandleStructure.EXCITING
            and candle.classification.direction == expected_direction
        )
        explosive_count = sum(item.explosive for item in aligned_exciting)
        width = max(zone.upper_price - zone.lower_price, 1e-9)
        total_body_ratio = sum(item.body for item in aligned_exciting) / width
        displacement = (
            max(0.0, evidence.qualifying_close - zone.upper_price)
            if zone.zone_type == ZoneType.DEMAND
            else max(0.0, zone.lower_price - evidence.qualifying_close)
        )
        displacement_ratio = displacement / width
        close_distances = [
            item.close_location
            for item in aligned_exciting
            if item.close_location is not None
        ]
        worst_close = max(close_distances, default=1.0)
        range_ratios = [
            item.range_to_median
            for item in aligned_exciting
            if item.range_to_median is not None
        ]
        average_range_ratio = (
            sum(range_ratios) / len(range_ratios) if range_ratios else 0.0
        )
        leg_in_body = sum(
            candle.classification.body for candle in evidence.leg_in_candles
        )
        leg_out_to_leg_in_ratio = (
            sum(item.body for item in aligned_exciting) / leg_in_body
            if leg_in_body > 0
            else 0.0
        )
        single = aligned_exciting[0] if len(aligned_exciting) == 1 else None

        explosive_path = (
            explosive_count >= 1
            and total_body_ratio >= self.EXPLOSIVE_MIN_BODY_TO_ZONE
            and displacement_ratio >= self.EXPLOSIVE_MIN_CLEARANCE_TO_ZONE
            and worst_close <= self.MAX_EXPLOSIVE_CLOSE_DISTANCE
            and evidence.closing_rule_passed
        )
        consecutive_strong = (
            len(evidence.leg_out_candles) >= 2
            and len(aligned_exciting) >= 2
            and all(
                item.classification.structure == CandleStructure.EXCITING
                and item.classification.direction == expected_direction
                for item in evidence.leg_out_candles[:2]
            )
        )
        multi_path = (
            consecutive_strong
            and total_body_ratio >= self.MULTI_MIN_BODY_TO_ZONE
            and displacement_ratio >= self.MULTI_MIN_CLEARANCE_TO_ZONE
            and average_range_ratio >= self.MIN_MULTI_RANGE_TO_MEDIAN
            and worst_close <= self.MAX_MULTI_CLOSE_DISTANCE
            and evidence.closing_rule_passed
        )
        single_path = bool(
            single is not None
            and len(evidence.leg_out_candles) == 1
            and not single.explosive
            and single.body_ratio >= self.SINGLE_MIN_BODY_RATIO
            and single.range_to_median is not None
            and single.range_to_median >= self.SINGLE_MIN_RANGE_TO_MEDIAN
            and single.close_location is not None
            and single.close_location <= self.SINGLE_MAX_CLOSE_DISTANCE
            and displacement_ratio >= self.SINGLE_MIN_CLEARANCE_TO_ZONE
            and leg_out_to_leg_in_ratio >= self.SINGLE_MIN_BODY_TO_LEG_IN
            and evidence.closing_rule_passed
        )
        if explosive_path or multi_path or single_path:
            if explosive_path:
                reason = "EXPLOSIVE_DEPARTURE"
                departure_quality = "EXPLOSIVE"
            elif multi_path:
                reason = "MULTI_CANDLE_STRONG_DEPARTURE"
                departure_quality = "STRONG"
            else:
                reason = "STRONG_SINGLE_EXCITING_DEPARTURE"
                departure_quality = "ACCEPTABLE"
            reasons.append(
                reason
            )
            reasons.append("CLOSING_RULE_PASSED")
            return self._result(
                True,
                reasons,
                departure_quality,
                "COMPACT",
                displacement,
                displacement_ratio,
                explosive_count,
                len(aligned_exciting),
                single,
                leg_out_to_leg_in_ratio,
                evidence.base_candle_count,
            )

        reasons.append("WEAK_DEPARTURE")
        if displacement_ratio < self.EXPLOSIVE_MIN_CLEARANCE_TO_ZONE:
            reasons.append("INSUFFICIENT_DISPLACEMENT")
        if worst_close > self.MAX_MULTI_CLOSE_DISTANCE:
            reasons.append("POOR_DIRECTIONAL_CLOSE")
        if len(evidence.leg_out_candles) >= 2 and not consecutive_strong:
            reasons.append("DRIFTING_DEPARTURE")
        if explosive_count == 0 and not multi_path:
            reasons.append("NO_EXPLOSIVE_OR_STRONG_SEQUENCE")
        if not evidence.closing_rule_passed:
            reasons.append("CLOSING_RULE_FAILED")
        return self._result(
            False,
            reasons,
            "WEAK",
            "COMPACT",
            displacement,
            displacement_ratio,
            explosive_count,
            len(aligned_exciting),
            single,
            leg_out_to_leg_in_ratio,
            evidence.base_candle_count,
        )

    def _rejected(self, reason: str) -> DashboardZoneQualification:
        return self._result(False, [reason], "MALFORMED", "UNKNOWN", 0, 0, 0, 0)

    @staticmethod
    def _result(
        qualified: bool,
        reasons: list[str],
        departure_quality: str,
        base_quality: str,
        displacement: float,
        ratio: float,
        explosive_count: int,
        aligned_count: int,
        single=None,
        leg_out_to_leg_in_ratio: float = 0.0,
        base_count: int = 0,
    ) -> DashboardZoneQualification:
        compactness = {
            1: ("EXCELLENT", "ONE_CANDLE_BASE", 0),
            2: ("STRONG", "TWO_CANDLE_BASE", 1),
            3: ("ACCEPTABLE", "THREE_CANDLE_BASE", 2),
        }.get(
            base_count,
            (
                "NOT_PRIMARY" if base_count >= 4 else "UNKNOWN",
                (
                    "BASE_TOO_LONG_FOR_PRIMARY_DASHBOARD"
                    if base_count >= 4
                    else "BASE_COUNT_UNAVAILABLE"
                ),
                3 if base_count >= 4 else 99,
            ),
        )
        return DashboardZoneQualification(
            dashboard_qualified=qualified,
            qualification_reason_codes=tuple(dict.fromkeys(reasons)),
            departure_quality=departure_quality,
            base_quality=base_quality,
            formation_quality="STRONG" if qualified else "NOT_PRIMARY",
            departure_displacement=round(displacement, 6),
            departure_zone_width_ratio=round(ratio, 6),
            explosive_candle_count=explosive_count,
            aligned_exciting_candle_count=aligned_count,
            leg_out_body_ratio=round(single.body_ratio, 6) if single else 0.0,
            leg_out_range_to_median=(
                round(single.range_to_median, 6)
                if single and single.range_to_median is not None
                else None
            ),
            directional_close_distance=(
                round(single.close_location, 6)
                if single and single.close_location is not None
                else None
            ),
            leg_out_to_leg_in_body_ratio=round(leg_out_to_leg_in_ratio, 6),
            base_candle_count=base_count,
            base_compactness=compactness[0],
            base_compactness_reason=compactness[1],
            base_preference_rank=compactness[2],
        )
