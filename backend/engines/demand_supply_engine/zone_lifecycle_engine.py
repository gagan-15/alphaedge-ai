"""Canonical, provider-independent demand/supply zone lifecycle evaluation.

Stage 1 infrastructure only: this module is not imported by production flows.
It deliberately does not replace the existing freshness implementation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from backend.models.zone_lifecycle import (
    LifecycleCandle,
    ZoneInteraction,
    ZoneInteractionType,
    ZoneInvalidationReason,
    ZoneLifecycleDefinition,
    ZoneLifecycleResult,
    ZoneLifecycleStatus,
    ZoneLifecycleType,
    ZoneVisit,
)


@dataclass(frozen=True)
class ZoneLifecycleConfig:
    """Calibratable lifecycle settings, separate from scoring."""

    approaching_percentage: float = 1.0
    approaching_atr_multiple: float | None = None
    mitigated_penetration_percent: float = 50.0

    def __post_init__(self) -> None:
        if self.approaching_percentage < 0:
            raise ValueError("Approaching percentage cannot be negative.")
        if (
            self.approaching_atr_multiple is not None
            and self.approaching_atr_multiple < 0
        ):
            raise ValueError("Approaching ATR multiple cannot be negative.")
        if not 0 <= self.mitigated_penetration_percent <= 100:
            raise ValueError("Mitigation threshold must be between 0 and 100.")


@dataclass
class _MutableVisit:
    visit_id: str
    start_index: int
    start_time: datetime
    end_index: int | None = None
    end_time: datetime | None = None
    maximum_penetration_percent: float = 0.0
    interaction_types: list[ZoneInteractionType] | None = None
    rejection_confirmed: bool = False
    respected: bool | None = None

    def __post_init__(self) -> None:
        if self.interaction_types is None:
            self.interaction_types = []

    def freeze(self) -> ZoneVisit:
        return ZoneVisit(
            visit_id=self.visit_id,
            start_index=self.start_index,
            start_time=self.start_time,
            end_index=self.end_index,
            end_time=self.end_time,
            maximum_penetration_percent=self.maximum_penetration_percent,
            interaction_types=tuple(self.interaction_types or ()),
            rejection_confirmed=self.rejection_confirmed,
            respected=self.respected,
        )


class ZoneLifecycleEngine:
    """Evaluate lifecycle facts without owning detection or scoring rules."""

    def __init__(self, config: ZoneLifecycleConfig | None = None) -> None:
        self._config = config or ZoneLifecycleConfig()

    def evaluate(
        self,
        zone: ZoneLifecycleDefinition,
        candles: Iterable[LifecycleCandle],
        *,
        current_price: float | None = None,
    ) -> ZoneLifecycleResult:
        """Evaluate candles from the explicit monitoring start onward."""

        ordered = sorted(candles, key=lambda candle: candle.index)
        self._validate_unique_indices(ordered)

        if not zone.activation.departure_confirmed:
            return self._empty_result(zone, ZoneLifecycleStatus.FORMING)

        monitored = [
            candle
            for candle in ordered
            if candle.index >= zone.activation.monitoring_start_index
        ]
        if not monitored:
            return self._empty_result(zone, ZoneLifecycleStatus.ACTIVATED)

        interactions: list[ZoneInteraction] = []
        visits: list[_MutableVisit] = []
        active_visit: _MutableVisit | None = None
        invalidated_at: datetime | None = None
        invalidation_reason: ZoneInvalidationReason | None = None
        latest_penetration = 0.0

        for candle in monitored:
            candle_types = self._interaction_types(zone, candle)
            inside_visit = self._enters_zone(zone, candle)

            if inside_visit and active_visit is None:
                active_visit = _MutableVisit(
                    visit_id=f"{zone.zone_id}:V{len(visits) + 1}",
                    start_index=candle.index,
                    start_time=candle.timestamp,
                )
                visits.append(active_visit)

            penetration = self.penetration_percent(zone, candle)
            latest_penetration = penetration if candle_types else 0.0
            if active_visit is not None:
                active_visit.maximum_penetration_percent = max(
                    active_visit.maximum_penetration_percent,
                    penetration,
                )
                for interaction_type in candle_types:
                    if interaction_type not in active_visit.interaction_types:
                        active_visit.interaction_types.append(interaction_type)

            for interaction_type in candle_types:
                interactions.append(
                    ZoneInteraction(
                        interaction_type=interaction_type,
                        candle_index=candle.index,
                        occurred_at=candle.timestamp,
                        price=self._interaction_price(
                            zone,
                            candle,
                            interaction_type,
                        ),
                        penetration_percent=penetration,
                        is_confirmed=self._is_confirmed(
                            candle,
                            interaction_type,
                        ),
                        visit_id=(
                            active_visit.visit_id
                            if active_visit is not None
                            else None
                        ),
                    )
                )

            if (
                ZoneInteractionType.DISTAL_CLOSE_BREACH in candle_types
                and candle.is_closed
            ):
                invalidated_at = candle.timestamp
                invalidation_reason = self._invalidation_reason(zone)
                if active_visit is not None:
                    active_visit.end_index = candle.index
                    active_visit.end_time = candle.timestamp
                    active_visit.respected = False
                    active_visit = None
                break

            if active_visit is not None and self._rejected_from_zone(zone, candle):
                active_visit.rejection_confirmed = True

            if active_visit is not None and self._fully_exited(zone, candle):
                active_visit.end_index = candle.index
                active_visit.end_time = candle.timestamp
                active_visit.respected = active_visit.rejection_confirmed
                active_visit = None

        frozen_visits = tuple(visit.freeze() for visit in visits)
        max_penetration = max(
            (
                visit.maximum_penetration_percent
                for visit in frozen_visits
            ),
            default=0.0,
        )
        structural_status = self._structural_status(
            visits=frozen_visits,
            active_visit=active_visit,
            max_penetration=max_penetration,
            invalidated=invalidated_at is not None,
        )
        is_fresh = len(interactions) == 0
        is_approaching = self._is_approaching(zone, current_price)
        lifecycle_status = (
            ZoneLifecycleStatus.APPROACHING
            if is_approaching
            and structural_status
            not in (
                ZoneLifecycleStatus.TESTING_NOW,
                ZoneLifecycleStatus.INVALIDATED,
            )
            else structural_status
        )

        return ZoneLifecycleResult(
            zone_id=zone.zone_id,
            symbol=zone.symbol,
            source_timeframe=zone.timeframe,
            lifecycle_status=lifecycle_status,
            structural_status=structural_status,
            is_fresh=is_fresh,
            is_approaching=is_approaching,
            test_count=len(frozen_visits),
            visit_count=len(frozen_visits),
            penetration_percent=latest_penetration,
            max_penetration_percent=max_penetration,
            current_interaction=self._current_interaction(
                interactions,
                monitored[-1].index,
            ),
            last_interaction=(
                interactions[-1].interaction_type if interactions else None
            ),
            last_tested_at=(
                interactions[-1].occurred_at if interactions else None
            ),
            invalidated_at=invalidated_at,
            invalidation_reason=invalidation_reason,
            interactions=tuple(interactions),
            visits=frozen_visits,
        )

    @staticmethod
    def penetration_percent(
        zone: ZoneLifecycleDefinition,
        candle: LifecycleCandle,
    ) -> float:
        """Return directional wick penetration as a percentage of zone width."""

        if zone.zone_type == ZoneLifecycleType.DEMAND:
            depth = zone.proximal - min(candle.low, zone.proximal)
        else:
            depth = max(candle.high, zone.proximal) - zone.proximal
        return max(0.0, (depth / zone.width) * 100.0)

    @staticmethod
    def _validate_unique_indices(candles: list[LifecycleCandle]) -> None:
        indices = [candle.index for candle in candles]
        if len(indices) != len(set(indices)):
            raise ValueError("Lifecycle candles must have unique indices.")

    @staticmethod
    def _enters_zone(
        zone: ZoneLifecycleDefinition,
        candle: LifecycleCandle,
    ) -> bool:
        if zone.zone_type == ZoneLifecycleType.DEMAND:
            return candle.low <= zone.proximal
        return candle.high >= zone.proximal

    @staticmethod
    def _fully_exited(
        zone: ZoneLifecycleDefinition,
        candle: LifecycleCandle,
    ) -> bool:
        if zone.zone_type == ZoneLifecycleType.DEMAND:
            return candle.low > zone.proximal
        return candle.high < zone.proximal

    @staticmethod
    def _rejected_from_zone(
        zone: ZoneLifecycleDefinition,
        candle: LifecycleCandle,
    ) -> bool:
        if not candle.is_closed:
            return False
        if zone.zone_type == ZoneLifecycleType.DEMAND:
            return candle.close > zone.proximal
        return candle.close < zone.proximal

    @staticmethod
    def _interaction_types(
        zone: ZoneLifecycleDefinition,
        candle: LifecycleCandle,
    ) -> tuple[ZoneInteractionType, ...]:
        if not ZoneLifecycleEngine._enters_zone(zone, candle):
            return ()

        result: list[ZoneInteractionType] = []
        penetration = ZoneLifecycleEngine.penetration_percent(zone, candle)
        if penetration == 0:
            result.append(ZoneInteractionType.PROXIMAL_TAG)
        else:
            result.append(ZoneInteractionType.WICK_TEST)

        body_low = min(candle.open, candle.close)
        body_high = max(candle.open, candle.close)
        zone_low = min(zone.proximal, zone.distal)
        zone_high = max(zone.proximal, zone.distal)
        if body_high >= zone_low and body_low <= zone_high:
            result.append(ZoneInteractionType.BODY_OVERLAP)
        if zone_low <= candle.close <= zone_high:
            result.append(ZoneInteractionType.CLOSE_INSIDE)

        distal_wick_breach = (
            candle.low < zone.distal
            if zone.zone_type == ZoneLifecycleType.DEMAND
            else candle.high > zone.distal
        )
        if distal_wick_breach:
            result.append(ZoneInteractionType.DISTAL_WICK_BREACH)

        distal_close_breach = (
            candle.close < zone.distal
            if zone.zone_type == ZoneLifecycleType.DEMAND
            else candle.close > zone.distal
        )
        if distal_close_breach:
            result.append(ZoneInteractionType.DISTAL_CLOSE_BREACH)
        return tuple(result)

    @staticmethod
    def _is_confirmed(
        candle: LifecycleCandle,
        interaction_type: ZoneInteractionType,
    ) -> bool:
        if interaction_type in (
            ZoneInteractionType.CLOSE_INSIDE,
            ZoneInteractionType.DISTAL_CLOSE_BREACH,
        ):
            return candle.is_closed
        return True

    @staticmethod
    def _interaction_price(
        zone: ZoneLifecycleDefinition,
        candle: LifecycleCandle,
        interaction_type: ZoneInteractionType,
    ) -> float:
        if interaction_type in (
            ZoneInteractionType.CLOSE_INSIDE,
            ZoneInteractionType.DISTAL_CLOSE_BREACH,
        ):
            return candle.close
        if interaction_type == ZoneInteractionType.PROXIMAL_TAG:
            return zone.proximal
        return (
            candle.low
            if zone.zone_type == ZoneLifecycleType.DEMAND
            else candle.high
        )

    @staticmethod
    def _invalidation_reason(
        zone: ZoneLifecycleDefinition,
    ) -> ZoneInvalidationReason:
        if zone.zone_type == ZoneLifecycleType.DEMAND:
            return ZoneInvalidationReason.DEMAND_CLOSE_BELOW_DISTAL
        return ZoneInvalidationReason.SUPPLY_CLOSE_ABOVE_DISTAL

    def _structural_status(
        self,
        *,
        visits: tuple[ZoneVisit, ...],
        active_visit: _MutableVisit | None,
        max_penetration: float,
        invalidated: bool,
    ) -> ZoneLifecycleStatus:
        if invalidated:
            return ZoneLifecycleStatus.INVALIDATED
        if active_visit is not None:
            return ZoneLifecycleStatus.TESTING_NOW
        if not visits:
            return ZoneLifecycleStatus.FRESH
        if max_penetration >= self._config.mitigated_penetration_percent:
            return ZoneLifecycleStatus.MITIGATED
        if len(visits) >= 2:
            return ZoneLifecycleStatus.RETESTED
        return ZoneLifecycleStatus.TESTED_RESPECTED

    def _is_approaching(
        self,
        zone: ZoneLifecycleDefinition,
        current_price: float | None,
    ) -> bool:
        if current_price is None:
            return False
        if zone.zone_type == ZoneLifecycleType.DEMAND:
            distance = max(0.0, current_price - zone.proximal)
        else:
            distance = max(0.0, zone.proximal - current_price)
        percentage_limit = (
            abs(current_price) * self._config.approaching_percentage / 100.0
        )
        limits = [percentage_limit]
        if (
            self._config.approaching_atr_multiple is not None
            and zone.atr is not None
        ):
            limits.append(
                zone.atr * self._config.approaching_atr_multiple
            )
        if zone.tick_size is not None:
            limits.append(zone.tick_size)
        return distance <= max(limits)

    @staticmethod
    def _current_interaction(
        interactions: list[ZoneInteraction],
        latest_candle_index: int,
    ) -> ZoneInteractionType | None:
        current = [
            interaction
            for interaction in interactions
            if interaction.candle_index == latest_candle_index
        ]
        return current[-1].interaction_type if current else None

    @staticmethod
    def _empty_result(
        zone: ZoneLifecycleDefinition,
        status: ZoneLifecycleStatus,
    ) -> ZoneLifecycleResult:
        return ZoneLifecycleResult(
            zone_id=zone.zone_id,
            symbol=zone.symbol,
            source_timeframe=zone.timeframe,
            lifecycle_status=status,
            structural_status=status,
            is_fresh=False,
            is_approaching=False,
            test_count=0,
            visit_count=0,
            penetration_percent=0.0,
            max_penetration_percent=0.0,
            current_interaction=None,
            last_interaction=None,
            last_tested_at=None,
            invalidated_at=None,
            invalidation_reason=None,
        )
