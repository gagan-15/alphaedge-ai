"""Canonical Body-to-Wick boundary calculation for detected zones."""

from __future__ import annotations

from collections.abc import Iterable

from pandas import DataFrame, Series

from backend.models.base_region import BaseRegion
from backend.models.departure import Departure
from backend.models.pattern import PatternType
from backend.models.zone import ZoneType
from backend.models.zone_boundary import (
    BoundaryMode,
    BoundaryReasonCode,
    BoundarySet,
    ExceptionalBoundarySource,
    ZoneBoundaryResult,
)
from backend.validators.zone_boundary_validator import ZoneBoundaryValidator


class ZoneBoundaryEngine:
    """Calculate boundaries without changing a zone's formation identity."""

    _DEMAND_PATTERNS = {
        PatternType.DROP_BASE_RALLY,
        PatternType.RALLY_BASE_RALLY,
    }
    _LEG_IN_EXCEPTIONAL_PATTERNS = {
        PatternType.DROP_BASE_RALLY,
        PatternType.RALLY_BASE_DROP,
    }
    _LEG_OUT_EXCEPTIONAL_PATTERNS = set(PatternType)

    def calculate(
        self,
        market_data: DataFrame,
        base: BaseRegion,
        pattern_type: PatternType,
        departure: Departure,
    ) -> ZoneBoundaryResult:
        """Return standard, alternate, exceptional and selected boundaries."""

        self._validate_input(market_data, base, departure)
        zone_type = self.zone_type_for(pattern_type)
        base_data = market_data.iloc[base.start_index : base.end_index + 1]
        body_highs = base_data[["Open", "Close"]].max(axis=1)
        body_lows = base_data[["Open", "Close"]].min(axis=1)

        if zone_type == ZoneType.DEMAND:
            standard = BoundarySet(
                proximal=float(body_highs.max()),
                distal=float(base_data["Low"].min()),
                mode=BoundaryMode.BODY_TO_WICK,
            )
            alternate = BoundarySet(
                proximal=float(base_data["High"].max()),
                distal=float(base_data["Low"].min()),
                mode=BoundaryMode.WICK_TO_WICK,
            )
        else:
            standard = BoundarySet(
                proximal=float(body_lows.min()),
                distal=float(base_data["High"].max()),
                mode=BoundaryMode.BODY_TO_WICK,
            )
            alternate = BoundarySet(
                proximal=float(base_data["Low"].min()),
                distal=float(base_data["High"].max()),
                mode=BoundaryMode.WICK_TO_WICK,
            )

        ZoneBoundaryValidator.validate(zone_type, standard)
        ZoneBoundaryValidator.validate(zone_type, alternate)
        exceptional = self._exceptional_boundary(
            market_data,
            base,
            pattern_type,
            departure,
            zone_type,
            standard,
        )
        if exceptional is not None:
            ZoneBoundaryValidator.validate(zone_type, exceptional)

        selected = exceptional or standard
        reasons = [
            BoundaryReasonCode.CANONICAL_BODY_TO_WICK,
            BoundaryReasonCode.ALTERNATE_WICK_TO_WICK,
        ]
        if exceptional is None:
            reasons.append(BoundaryReasonCode.EXCEPTIONAL_NOT_QUALIFIED)
        elif exceptional.exceptional_source == ExceptionalBoundarySource.LEG_IN:
            reasons.append(BoundaryReasonCode.EXCEPTIONAL_LEG_IN_OVERLAP)
        else:
            reasons.append(BoundaryReasonCode.EXCEPTIONAL_LEG_OUT_OVERLAP)
        return ZoneBoundaryResult(
            standard=standard,
            wick_to_wick=alternate,
            exceptional=exceptional,
            selected=selected,
            reason_codes=tuple(reasons),
        )

    @classmethod
    def zone_type_for(cls, pattern_type: PatternType) -> ZoneType:
        return (
            ZoneType.DEMAND
            if pattern_type in cls._DEMAND_PATTERNS
            else ZoneType.SUPPLY
        )

    def _exceptional_boundary(
        self,
        market_data: DataFrame,
        base: BaseRegion,
        pattern_type: PatternType,
        departure: Departure,
        zone_type: ZoneType,
        standard: BoundarySet,
    ) -> BoundarySet | None:
        candidates: list[tuple[float, ExceptionalBoundarySource]] = []
        if (
            pattern_type in self._LEG_IN_EXCEPTIONAL_PATTERNS
            and departure.leg_in_end_index is not None
        ):
            candle = market_data.iloc[departure.leg_in_end_index]
            candidate = self._overlapping_extreme(candle, market_data, base, zone_type)
            if self._extends_distal(candidate, standard.distal, zone_type):
                candidates.append((candidate, ExceptionalBoundarySource.LEG_IN))
        if pattern_type in self._LEG_OUT_EXCEPTIONAL_PATTERNS:
            candle = market_data.iloc[departure.departure_index]
            candidate = self._overlapping_extreme(candle, market_data, base, zone_type)
            if self._extends_distal(candidate, standard.distal, zone_type):
                candidates.append((candidate, ExceptionalBoundarySource.LEG_OUT))
        if not candidates:
            return None
        distal, source = (
            min(candidates, key=lambda item: item[0])
            if zone_type == ZoneType.DEMAND
            else max(candidates, key=lambda item: item[0])
        )
        return BoundarySet(
            proximal=standard.proximal,
            distal=distal,
            mode=BoundaryMode.EXCEPTIONAL,
            exceptional_source=source,
        )

    @staticmethod
    def _overlapping_extreme(
        candle: Series,
        market_data: DataFrame,
        base: BaseRegion,
        zone_type: ZoneType,
    ) -> float:
        base_data = market_data.iloc[base.start_index : base.end_index + 1]
        base_low = float(base_data["Low"].min())
        base_high = float(base_data["High"].max())
        candle_low = float(candle["Low"])
        candle_high = float(candle["High"])
        overlaps = candle_low <= base_high and candle_high >= base_low
        if not overlaps:
            return float("nan")
        return candle_low if zone_type == ZoneType.DEMAND else candle_high

    @staticmethod
    def _extends_distal(
        candidate: float, standard_distal: float, zone_type: ZoneType
    ) -> bool:
        if candidate != candidate:  # NaN
            return False
        return (
            candidate < standard_distal
            if zone_type == ZoneType.DEMAND
            else candidate > standard_distal
        )

    @staticmethod
    def _validate_input(
        market_data: DataFrame, base: BaseRegion, departure: Departure
    ) -> None:
        if not isinstance(market_data, DataFrame):
            raise TypeError("market_data must be a pandas DataFrame.")
        if market_data.empty:
            raise ValueError("market_data cannot be empty.")
        missing = [
            column
            for column in ("Open", "High", "Low", "Close")
            if column not in market_data.columns
        ]
        if missing:
            raise ValueError("Missing OHLC columns: " + ", ".join(missing))
        if not isinstance(base, BaseRegion):
            raise TypeError("base must be a BaseRegion.")
        if not isinstance(departure, Departure):
            raise TypeError("departure must be a Departure.")
        indexes: Iterable[int | None] = (
            base.start_index,
            base.end_index,
            departure.departure_index,
            departure.leg_in_end_index,
        )
        if any(index is not None and index >= len(market_data) for index in indexes):
            raise IndexError("Boundary source index is outside market_data.")
