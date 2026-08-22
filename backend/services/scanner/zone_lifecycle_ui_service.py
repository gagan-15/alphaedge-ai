"""Read-only UI projection of canonical lifecycle and authenticity records.

This service deliberately owns no trading rules. It adapts already detected
zones and OHLC candles to the approved canonical engines, then serializes the
facts required by the scanner and stock-details UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pandas import DataFrame, Timestamp

from backend.engines.demand_supply_engine.zone_authenticity_engine import (
    ZoneAuthenticityEngine,
)
from backend.engines.demand_supply_engine.zone_lifecycle_engine import (
    ZoneLifecycleEngine,
)
from backend.models.zone import Zone, ZoneType
from backend.models.zone_authenticity import (
    AuthenticityReasonCode,
    ZoneRelationshipType,
)
from backend.models.zone_lifecycle import (
    LifecycleCandle,
    ZoneActivation,
    ZoneLifecycleDefinition,
    ZoneLifecycleType,
)
from backend.services.scanner.dashboard_lifecycle_eligibility_service import (
    DashboardLifecycleEligibilityService,
)


@dataclass(frozen=True)
class ZoneUiMetadata:
    """Canonical facts displayed by the UI for one detected zone."""

    zone_id: str
    lifecycle_status: str
    authenticity_status: str
    authenticity_reason_code: str
    authenticity_reason: str
    test_count: int
    visit_count: int
    is_fresh: bool
    is_invalidated: bool
    dashboard_lifecycle_eligible: bool
    dashboard_lifecycle_reason_code: str
    reaction_status: str
    reaction_percentage: float
    max_penetration_percent: float
    current_penetration_percent: float
    good_closing: bool | None
    parent_zone_id: str | None
    is_nested: bool
    is_duplicate: bool
    overlap_percent: float | None


class ZoneLifecycleUiService:
    """Run approved canonical engines without changing production detection."""

    def __init__(self) -> None:
        self._lifecycle = ZoneLifecycleEngine()
        self._authenticity = ZoneAuthenticityEngine()
        self._dashboard_policy = DashboardLifecycleEligibilityService()

    def evaluate(
        self,
        zones: list[Zone],
        data: DataFrame,
        *,
        symbol: str,
        timeframe: str,
        current_price: float,
    ) -> dict[int, ZoneUiMetadata]:
        if not zones or data.empty:
            return {}

        candles = tuple(self._candles(data))
        lifecycle_by_index = {}
        active_indexes: set[int] = set()
        for zone in zones:
            result = self._lifecycle.evaluate(
                self._definition(zone, data, symbol, timeframe),
                candles,
                current_price=current_price,
            )
            lifecycle_by_index[zone.created_index] = result
            if result.is_active:
                active_indexes.add(zone.created_index)

        authenticity = self._authenticity.classify(
            zones,
            data,
            symbol=symbol,
            timeframe=timeframe,
            active_zone_indexes=active_indexes,
        )
        authenticity_by_index = {
            record.zone.created_index: record for record in authenticity
        }

        metadata: dict[int, ZoneUiMetadata] = {}
        for zone in zones:
            lifecycle = lifecycle_by_index[zone.created_index]
            dashboard_policy = self._dashboard_policy.evaluate(lifecycle)
            authentic = authenticity_by_index[zone.created_index]
            overlaps = [
                relation.overlap_percent
                for relation in authentic.relationships
                if relation.relationship_type == ZoneRelationshipType.OVERLAPPING
                and relation.overlap_percent is not None
            ]
            metadata[zone.created_index] = ZoneUiMetadata(
                zone_id=authentic.zone_id,
                lifecycle_status=lifecycle.lifecycle_status.value,
                authenticity_status=authentic.status.value,
                authenticity_reason_code=authentic.reason_code.value,
                authenticity_reason=authentic.reason,
                test_count=lifecycle.test_count,
                visit_count=lifecycle.visit_count,
                is_fresh=lifecycle.is_fresh,
                is_invalidated=(
                    lifecycle.lifecycle_status.value in ("INVALIDATED", "REMOVED")
                    or lifecycle.is_removed
                ),
                dashboard_lifecycle_eligible=dashboard_policy.eligible,
                dashboard_lifecycle_reason_code=dashboard_policy.reason_code,
                reaction_status=(
                    "REACTING" if lifecycle.is_reacting else "NOT_REACTING"
                ),
                reaction_percentage=round(lifecycle.reaction_percentage, 2),
                max_penetration_percent=round(lifecycle.max_penetration_percent, 2),
                current_penetration_percent=round(lifecycle.penetration_percent, 2),
                good_closing=authentic.good_closing,
                parent_zone_id=authentic.parent_zone_id,
                is_nested=authentic.reason_code == AuthenticityReasonCode.NESTED,
                is_duplicate=authentic.reason_code == AuthenticityReasonCode.DUPLICATE,
                overlap_percent=max(overlaps) if overlaps else None,
            )
        return metadata

    @staticmethod
    def _candles(data: DataFrame):
        for index, (timestamp, row) in enumerate(data.iterrows()):
            yield LifecycleCandle(
                index=index,
                timestamp=ZoneLifecycleUiService._datetime(timestamp),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
            )

    @staticmethod
    def _definition(
        zone: Zone,
        data: DataFrame,
        symbol: str,
        timeframe: str,
    ) -> ZoneLifecycleDefinition:
        evidence = zone.formation_evidence
        formation_start_index = (
            evidence.leg_in_start_index if evidence else zone.created_index
        )
        formation_end_index = (
            evidence.base_end_index if evidence else zone.created_index
        )
        departure_index = min(
            evidence.leg_out_end_index if evidence else zone.created_index + 1,
            len(data) - 1,
        )
        monitoring_index = min(departure_index + 1, len(data))
        departure_confirmed = monitoring_index < len(data)
        activation = ZoneActivation(
            formation_start_index=formation_start_index,
            formation_end_index=formation_end_index,
            departure_confirmation_index=(
                departure_index if departure_confirmed else None
            ),
            activation_index=(departure_index if departure_confirmed else None),
            monitoring_start_index=(monitoring_index if departure_confirmed else None),
            departure_confirmed=departure_confirmed,
            activation_time=(
                ZoneLifecycleUiService._datetime(data.index[departure_index])
                if departure_confirmed
                else None
            ),
        )
        return ZoneLifecycleDefinition(
            zone_id=f"{symbol}:{timeframe}:{zone.created_index}",
            symbol=symbol,
            timeframe=timeframe,
            zone_type=(
                ZoneLifecycleType.DEMAND
                if zone.zone_type == ZoneType.DEMAND
                else ZoneLifecycleType.SUPPLY
            ),
            proximal=(
                zone.upper_price
                if zone.zone_type == ZoneType.DEMAND
                else zone.lower_price
            ),
            distal=(
                zone.lower_price
                if zone.zone_type == ZoneType.DEMAND
                else zone.upper_price
            ),
            activation=activation,
        )

    @staticmethod
    def _datetime(value: object) -> datetime:
        if isinstance(value, datetime):
            return value
        return Timestamp(value).to_pydatetime()
