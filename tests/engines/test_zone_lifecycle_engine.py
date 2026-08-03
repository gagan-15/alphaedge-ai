"""Stage 1 unit tests for the isolated canonical ZoneLifecycleEngine."""

from datetime import datetime, timedelta, timezone

import pytest

from backend.engines.demand_supply_engine.zone_lifecycle_engine import (
    ZoneLifecycleConfig,
    ZoneLifecycleEngine,
)
from backend.models.zone_lifecycle import (
    LifecycleCandle,
    ZoneActivation,
    ZoneInteractionType,
    ZoneInvalidationReason,
    ZoneLifecycleDefinition,
    ZoneLifecycleStatus,
    ZoneLifecycleType,
)


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def candle(
    index: int,
    open_price: float,
    high: float,
    low: float,
    close: float,
    *,
    is_closed: bool = True,
) -> LifecycleCandle:
    return LifecycleCandle(
        index=index,
        timestamp=BASE_TIME + timedelta(days=index),
        open=open_price,
        high=high,
        low=low,
        close=close,
        is_closed=is_closed,
    )


def activation(*, confirmed: bool = True) -> ZoneActivation:
    return ZoneActivation(
        formation_start_index=0,
        formation_end_index=1,
        departure_confirmation_index=2 if confirmed else None,
        activation_index=2 if confirmed else None,
        monitoring_start_index=3 if confirmed else None,
        departure_confirmed=confirmed,
        activation_time=BASE_TIME + timedelta(days=2) if confirmed else None,
    )


def demand_zone(
    *,
    zone_activation: ZoneActivation | None = None,
) -> ZoneLifecycleDefinition:
    return ZoneLifecycleDefinition(
        zone_id="TCS:1D:DZ1",
        symbol="TCS",
        timeframe="1D",
        zone_type=ZoneLifecycleType.DEMAND,
        proximal=110.0,
        distal=100.0,
        activation=zone_activation or activation(),
        tick_size=0.05,
        atr=5.0,
    )


def supply_zone() -> ZoneLifecycleDefinition:
    return ZoneLifecycleDefinition(
        zone_id="INFY:1D:SZ1",
        symbol="INFY",
        timeframe="1D",
        zone_type=ZoneLifecycleType.SUPPLY,
        proximal=100.0,
        distal=110.0,
        activation=activation(),
    )


class TestLifecycleStates:
    def test_unconfirmed_zone_is_forming(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(zone_activation=activation(confirmed=False)),
            [],
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.FORMING
        assert result.structural_status == ZoneLifecycleStatus.FORMING

    def test_confirmed_zone_without_monitored_candles_is_activated(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [candle(2, 112, 120, 111, 118)],
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.ACTIVATED

    def test_untouched_zone_is_fresh(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [candle(3, 115, 120, 111, 118)],
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.FRESH
        assert result.is_fresh is True
        assert result.visit_count == 0

    def test_current_visit_is_testing_now(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [candle(3, 112, 114, 108, 109)],
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.TESTING_NOW
        assert result.is_fresh is False
        assert result.visit_count == 1

    def test_completed_first_visit_is_tested_respected(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [
                candle(3, 112, 114, 108, 112),
                candle(4, 113, 118, 111, 117),
            ],
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.TESTED_RESPECTED
        assert result.visits[0].rejection_confirmed is True
        assert result.visits[0].respected is True

    def test_two_separate_visits_are_retested(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [
                candle(3, 112, 114, 109, 112),
                candle(4, 113, 116, 111, 115),
                candle(5, 112, 114, 108, 112),
                candle(6, 113, 117, 111, 116),
            ],
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.RETESTED
        assert result.visit_count == 2
        assert result.test_count == 2
        assert result.visits[0].visit_id.endswith(":V1")
        assert result.visits[1].visit_id.endswith(":V2")

    def test_deep_non_invalidating_visit_is_mitigated(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [
                candle(3, 112, 114, 104, 112),
                candle(4, 113, 116, 111, 115),
            ],
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.MITIGATED
        assert result.max_penetration_percent == pytest.approx(60.0)

    def test_approaching_is_independent_from_freshness(self) -> None:
        engine = ZoneLifecycleEngine(
            ZoneLifecycleConfig(approaching_percentage=1.0)
        )
        result = engine.evaluate(
            demand_zone(),
            [candle(3, 115, 120, 111, 118)],
            current_price=110.5,
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.APPROACHING
        assert result.structural_status == ZoneLifecycleStatus.FRESH
        assert result.is_fresh is True
        assert result.is_approaching is True


class TestInteractionsAndPenetration:
    @pytest.mark.parametrize(
        ("low", "expected"),
        [
            (110.0, 0.0),
            (109.9, 1.0),
            (107.5, 25.0),
            (105.0, 50.0),
            (100.0, 100.0),
        ],
    )
    def test_demand_penetration_formula(
        self,
        low: float,
        expected: float,
    ) -> None:
        observed = ZoneLifecycleEngine.penetration_percent(
            demand_zone(),
            candle(3, 112, 115, low, 112),
        )

        assert observed == pytest.approx(expected)

    @pytest.mark.parametrize(
        ("high", "expected"),
        [
            (100.0, 0.0),
            (100.1, 1.0),
            (102.5, 25.0),
            (105.0, 50.0),
            (110.0, 100.0),
        ],
    )
    def test_supply_penetration_formula(
        self,
        high: float,
        expected: float,
    ) -> None:
        observed = ZoneLifecycleEngine.penetration_percent(
            supply_zone(),
            candle(3, 98, high, 95, 98),
        )

        assert observed == pytest.approx(expected)

    def test_exact_proximal_wick_tag_is_recorded_and_not_fresh(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [candle(3, 112, 114, 110, 112)],
        )

        assert result.is_fresh is False
        assert result.last_interaction == ZoneInteractionType.PROXIMAL_TAG
        assert result.max_penetration_percent == 0.0

    def test_wick_body_and_close_interactions_are_separate(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [candle(3, 108, 112, 104, 106)],
        )
        types = {
            interaction.interaction_type
            for interaction in result.interactions
        }

        assert ZoneInteractionType.WICK_TEST in types
        assert ZoneInteractionType.BODY_OVERLAP in types
        assert ZoneInteractionType.CLOSE_INSIDE in types

    def test_consecutive_inside_candles_count_as_one_visit(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [
                candle(3, 109, 112, 106, 108),
                candle(4, 108, 111, 104, 107),
                candle(5, 112, 116, 111, 115),
            ],
        )

        assert result.visit_count == 1
        assert result.visits[0].start_index == 3
        assert result.visits[0].end_index == 5
        assert result.visits[0].maximum_penetration_percent == 60.0

    def test_formation_and_activation_candles_are_not_monitored(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [
                candle(0, 105, 110, 100, 108),
                candle(1, 108, 112, 104, 111),
                candle(2, 111, 120, 109, 118),
                candle(3, 115, 120, 111, 118),
            ],
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.FRESH
        assert result.interactions == ()


class TestInvalidation:
    def test_demand_distal_wick_breach_with_recovery_is_not_invalidated(
        self,
    ) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [
                candle(3, 108, 113, 98, 105),
                candle(4, 112, 116, 111, 115),
            ],
        )
        types = {
            interaction.interaction_type
            for interaction in result.interactions
        }

        assert ZoneInteractionType.DISTAL_WICK_BREACH in types
        assert result.lifecycle_status == ZoneLifecycleStatus.MITIGATED
        assert result.invalidated_at is None

    def test_demand_closed_below_distal_is_invalidated(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [candle(3, 105, 108, 95, 98)],
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.INVALIDATED
        assert (
            result.invalidation_reason
            == ZoneInvalidationReason.DEMAND_CLOSE_BELOW_DISTAL
        )
        assert result.invalidated_at == BASE_TIME + timedelta(days=3)

    def test_supply_closed_above_distal_is_invalidated(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            supply_zone(),
            [candle(3, 105, 115, 102, 112)],
        )

        assert result.lifecycle_status == ZoneLifecycleStatus.INVALIDATED
        assert (
            result.invalidation_reason
            == ZoneInvalidationReason.SUPPLY_CLOSE_ABOVE_DISTAL
        )

    def test_unfinished_distal_close_breach_is_pending(self) -> None:
        result = ZoneLifecycleEngine().evaluate(
            demand_zone(),
            [candle(3, 105, 108, 95, 98, is_closed=False)],
        )
        close_breach = next(
            interaction
            for interaction in result.interactions
            if interaction.interaction_type
            == ZoneInteractionType.DISTAL_CLOSE_BREACH
        )

        assert close_breach.is_confirmed is False
        assert result.lifecycle_status == ZoneLifecycleStatus.TESTING_NOW
        assert result.invalidated_at is None


class TestValidation:
    def test_demand_boundaries_must_be_directionally_valid(self) -> None:
        with pytest.raises(ValueError, match="Demand proximal"):
            ZoneLifecycleDefinition(
                zone_id="bad",
                symbol="TCS",
                timeframe="1D",
                zone_type=ZoneLifecycleType.DEMAND,
                proximal=100,
                distal=110,
                activation=activation(),
            )

    def test_supply_boundaries_must_be_directionally_valid(self) -> None:
        with pytest.raises(ValueError, match="Supply proximal"):
            ZoneLifecycleDefinition(
                zone_id="bad",
                symbol="TCS",
                timeframe="1D",
                zone_type=ZoneLifecycleType.SUPPLY,
                proximal=110,
                distal=100,
                activation=activation(),
            )

    def test_activation_requires_explicit_monitoring_boundary(self) -> None:
        with pytest.raises(ValueError, match="Monitoring must begin"):
            ZoneActivation(
                formation_start_index=0,
                formation_end_index=1,
                departure_confirmation_index=2,
                activation_index=2,
                monitoring_start_index=2,
                departure_confirmed=True,
            )

    def test_duplicate_candle_indices_are_rejected(self) -> None:
        duplicate = candle(3, 112, 115, 111, 114)
        with pytest.raises(ValueError, match="unique indices"):
            ZoneLifecycleEngine().evaluate(
                demand_zone(),
                [duplicate, duplicate],
            )
