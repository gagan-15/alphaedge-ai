"""Canonical authenticity classification for already-formed zones."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from math import isfinite

from pandas import DataFrame

from backend.models.zone import Zone, ZoneType
from backend.models.zone_authenticity import (
    AuthenticityReasonCode,
    AuthenticityStatus,
    FormationEvidence,
    ReactionSource,
    ZoneAuthenticityRecord,
    ZoneRelationship,
    ZoneRelationshipType,
)


@dataclass
class _WorkingRecord:
    zone: Zone
    zone_id: str
    occurrence_id: str
    canonical_origin: str
    proximal: float
    distal: float
    active: bool
    status: AuthenticityStatus = AuthenticityStatus.AUTHENTIC
    reason_code: AuthenticityReasonCode = AuthenticityReasonCode.ORIGINAL
    reason: str = "Original zone with no authenticity conflicts."
    parent_zone_id: str | None = None
    child_zone_ids: list[str] = field(default_factory=list)
    reaction_depth_percent: float | None = None
    reaction_timestamp: str | None = None
    reaction_source: ReactionSource | None = None
    duplicate_of_zone_id: str | None = None
    good_closing: bool | None = None
    relationships: list[ZoneRelationship] = field(default_factory=list)


class ZoneAuthenticityEngine:
    """Classify authenticity without changing formation, boundaries or lifecycle."""

    def classify(
        self,
        zones: list[Zone],
        market_data: DataFrame,
        *,
        symbol: str,
        timeframe: str,
        tick_size: float = 0.05,
        formation_evidence: dict[int, FormationEvidence] | None = None,
        active_zone_indexes: set[int] | None = None,
    ) -> list[ZoneAuthenticityRecord]:
        """Return one authenticity record for every supplied zone occurrence."""

        self._validate_input(zones, market_data, symbol, timeframe, tick_size)
        evidence = formation_evidence or {}
        ordered = sorted(
            enumerate(zones),
            key=lambda item: (item[1].created_index, item[0]),
        )
        working: list[_WorkingRecord] = []
        identity_counts: dict[str, int] = {}

        for _, zone in ordered:
            proximal, distal = self._normalized_boundaries(zone, tick_size)
            origin = self._origin(market_data, zone.created_index)
            zone_id = self._identity(
                symbol,
                timeframe,
                zone,
                origin,
                proximal,
                distal,
            )
            identity_counts[zone_id] = identity_counts.get(zone_id, 0) + 1
            current = _WorkingRecord(
                zone=zone,
                zone_id=zone_id,
                occurrence_id=f"{zone_id}:O{identity_counts[zone_id]}",
                canonical_origin=origin,
                proximal=proximal,
                distal=distal,
                active=(
                    active_zone_indexes is None
                    or zone.created_index in active_zone_indexes
                ),
                good_closing=self._good_closing(
                    zone,
                    market_data,
                    evidence.get(zone.created_index),
                ),
            )

            duplicate = self._duplicate(current, working)
            if duplicate is not None:
                self._mark_non_authentic(
                    current,
                    AuthenticityReasonCode.DUPLICATE,
                    "Duplicate of the same canonical zone identity.",
                )
                current.duplicate_of_zone_id = duplicate.zone_id
                current.relationships.append(
                    ZoneRelationship(
                        ZoneRelationshipType.DUPLICATE,
                        duplicate.zone_id,
                        100.0,
                    )
                )
                working.append(current)
                continue

            reaction = self._reaction_parent(current, working, market_data)
            if reaction is not None:
                parent, depth, source = reaction
                current.parent_zone_id = parent.zone_id
                current.reaction_depth_percent = depth
                current.reaction_timestamp = origin
                current.reaction_source = source
                current.relationships.append(
                    ZoneRelationship(
                        ZoneRelationshipType.REACTION_PARENT,
                        parent.zone_id,
                        depth,
                    )
                )
                self._add_child(parent, current.zone_id)
                self._mark_non_authentic(
                    current,
                    AuthenticityReasonCode.REACTION,
                    "Zone formed as a reaction from an earlier active zone.",
                )

            self._classify_geometric_relationships(current, working)
            working.append(current)

        return [self._freeze(item, symbol, timeframe) for item in working]

    def _classify_geometric_relationships(
        self, current: _WorkingRecord, earlier: list[_WorkingRecord]
    ) -> None:
        for related in earlier:
            if related.zone.zone_type != current.zone.zone_type:
                continue
            overlap = self._overlap_percent(current, related)
            if overlap <= 0:
                continue
            current_inside = self._contains(related, current)
            related_inside = self._contains(current, related)
            if current_inside or related_inside:
                parent, child = (
                    (related, current) if current_inside else (current, related)
                )
                self._add_child(parent, child.zone_id)
                child.parent_zone_id = child.parent_zone_id or parent.zone_id
                child.relationships.append(
                    ZoneRelationship(
                        ZoneRelationshipType.NESTED_PARENT,
                        parent.zone_id,
                        overlap,
                    )
                )
                parent.relationships.append(
                    ZoneRelationship(
                        ZoneRelationshipType.NESTED_CHILD,
                        child.zone_id,
                        overlap,
                    )
                )
                if child is current and current.status == AuthenticityStatus.AUTHENTIC:
                    self._mark_non_authentic(
                        current,
                        AuthenticityReasonCode.NESTED,
                        "Zone is nested inside an earlier canonical zone.",
                    )
                continue
            current.relationships.append(
                ZoneRelationship(
                    ZoneRelationshipType.OVERLAPPING,
                    related.zone_id,
                    overlap,
                )
            )
            related.relationships.append(
                ZoneRelationship(
                    ZoneRelationshipType.OVERLAPPING,
                    current.zone_id,
                    overlap,
                )
            )
            if current.status == AuthenticityStatus.AUTHENTIC:
                self._mark_non_authentic(
                    current,
                    AuthenticityReasonCode.OVERLAPPING,
                    "Zone partially overlaps an earlier canonical zone.",
                )

    def _reaction_parent(
        self,
        current: _WorkingRecord,
        earlier: list[_WorkingRecord],
        market_data: DataFrame,
    ) -> tuple[_WorkingRecord, float, ReactionSource] | None:
        candle = market_data.iloc[current.zone.created_index]
        candle_low = float(candle["Low"])
        candle_high = float(candle["High"])
        body_low = min(float(candle["Open"]), float(candle["Close"]))
        body_high = max(float(candle["Open"]), float(candle["Close"]))
        for parent in reversed(earlier):
            if (
                parent.zone.zone_type != current.zone.zone_type
                or not parent.active
            ):
                continue
            parent_low, parent_high = self._price_range(parent)
            overlap = max(
                0.0,
                min(candle_high, parent_high) - max(candle_low, parent_low),
            )
            if overlap <= 0:
                continue
            body_overlap = max(
                0.0,
                min(body_high, parent_high) - max(body_low, parent_low),
            )
            depth = round(overlap / (parent_high - parent_low) * 100.0, 4)
            source = ReactionSource.BODY if body_overlap > 0 else ReactionSource.WICK
            return parent, depth, source
        return None

    @staticmethod
    def _good_closing(
        zone: Zone,
        market_data: DataFrame,
        evidence: FormationEvidence | None,
    ) -> bool | None:
        if evidence is None:
            return None
        indexes = (
            evidence.leg_in_start_index,
            evidence.leg_in_end_index,
            evidence.departure_index,
        )
        if min(indexes) < 0 or max(indexes) >= len(market_data):
            return None
        leg_in = market_data.iloc[
            evidence.leg_in_start_index : evidence.leg_in_end_index + 1
        ]
        departure_close = float(
            market_data.iloc[evidence.departure_index]["Close"]
        )
        if zone.zone_type == ZoneType.DEMAND:
            return departure_close > float(leg_in["High"].max())
        return departure_close < float(leg_in["Low"].min())

    @staticmethod
    def _duplicate(
        current: _WorkingRecord, earlier: list[_WorkingRecord]
    ) -> _WorkingRecord | None:
        return next(
            (item for item in earlier if item.zone_id == current.zone_id),
            None,
        )

    @staticmethod
    def _contains(parent: _WorkingRecord, child: _WorkingRecord) -> bool:
        parent_low, parent_high = ZoneAuthenticityEngine._price_range(parent)
        child_low, child_high = ZoneAuthenticityEngine._price_range(child)
        return (
            parent_low <= child_low
            and parent_high >= child_high
            and (parent_low < child_low or parent_high > child_high)
        )

    @staticmethod
    def _overlap_percent(left: _WorkingRecord, right: _WorkingRecord) -> float:
        left_low, left_high = ZoneAuthenticityEngine._price_range(left)
        right_low, right_high = ZoneAuthenticityEngine._price_range(right)
        overlap = max(0.0, min(left_high, right_high) - max(left_low, right_low))
        smaller_width = min(left_high - left_low, right_high - right_low)
        return 0.0 if smaller_width <= 0 else round(overlap / smaller_width * 100.0, 4)

    @staticmethod
    def _price_range(record: _WorkingRecord) -> tuple[float, float]:
        return min(record.proximal, record.distal), max(
            record.proximal, record.distal
        )

    @staticmethod
    def _add_child(parent: _WorkingRecord, child_zone_id: str) -> None:
        if child_zone_id not in parent.child_zone_ids:
            parent.child_zone_ids.append(child_zone_id)

    @staticmethod
    def _mark_non_authentic(
        record: _WorkingRecord,
        reason_code: AuthenticityReasonCode,
        reason: str,
    ) -> None:
        record.status = AuthenticityStatus.NON_AUTHENTIC
        record.reason_code = reason_code
        record.reason = reason

    @staticmethod
    def _normalized_boundaries(zone: Zone, tick_size: float) -> tuple[float, float]:
        tick = Decimal(str(tick_size))

        def normalize(value: float) -> float:
            ticks = (Decimal(str(value)) / tick).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
            return float(ticks * tick)

        if zone.zone_type == ZoneType.DEMAND:
            return normalize(zone.upper_price), normalize(zone.lower_price)
        return normalize(zone.lower_price), normalize(zone.upper_price)

    @staticmethod
    def _origin(market_data: DataFrame, index: int) -> str:
        value = market_data.index[index]
        return value.isoformat() if hasattr(value, "isoformat") else str(value)

    @staticmethod
    def _identity(
        symbol: str,
        timeframe: str,
        zone: Zone,
        origin: str,
        proximal: float,
        distal: float,
    ) -> str:
        source = "|".join(
            (
                symbol.upper(),
                timeframe.upper(),
                zone.pattern_type or "UNKNOWN",
                origin,
                f"{proximal:.10f}",
                f"{distal:.10f}",
            )
        )
        return "ZONE-" + sha256(source.encode("utf-8")).hexdigest()[:20].upper()

    @staticmethod
    def _freeze(
        record: _WorkingRecord, symbol: str, timeframe: str
    ) -> ZoneAuthenticityRecord:
        return ZoneAuthenticityRecord(
            zone=record.zone,
            zone_id=record.zone_id,
            occurrence_id=record.occurrence_id,
            symbol=symbol.upper(),
            timeframe=timeframe.upper(),
            status=record.status,
            reason_code=record.reason_code,
            reason=record.reason,
            canonical_origin=record.canonical_origin,
            normalized_proximal=record.proximal,
            normalized_distal=record.distal,
            parent_zone_id=record.parent_zone_id,
            child_zone_ids=tuple(record.child_zone_ids),
            reaction_depth_percent=record.reaction_depth_percent,
            reaction_timestamp=record.reaction_timestamp,
            reaction_source=record.reaction_source,
            duplicate_of_zone_id=record.duplicate_of_zone_id,
            good_closing=record.good_closing,
            relationships=tuple(record.relationships),
        )

    @staticmethod
    def _validate_input(
        zones: list[Zone],
        market_data: DataFrame,
        symbol: str,
        timeframe: str,
        tick_size: float,
    ) -> None:
        invalid_zones = not isinstance(zones, list) or any(
            not isinstance(zone, Zone) for zone in zones
        )
        if invalid_zones:
            raise TypeError("zones must be a list of Zone objects.")
        if not isinstance(market_data, DataFrame) or market_data.empty:
            raise ValueError("market_data must be a non-empty pandas DataFrame.")
        missing = [
            column
            for column in ("Open", "High", "Low", "Close")
            if column not in market_data.columns
        ]
        if missing:
            raise ValueError("Missing OHLC columns: " + ", ".join(missing))
        if not symbol.strip() or not timeframe.strip():
            raise ValueError("symbol and timeframe are required.")
        if not isfinite(tick_size) or tick_size <= 0:
            raise ValueError("tick_size must be a positive finite number.")
        invalid_origins = any(
            zone.created_index < 0 or zone.created_index >= len(market_data)
            for zone in zones
        )
        if invalid_origins:
            raise IndexError("Zone origin is outside market_data.")
