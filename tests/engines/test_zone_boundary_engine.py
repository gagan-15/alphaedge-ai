"""Milestone 2 tests for canonical zone boundaries."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from backend.engines.demand_supply_engine.zone_boundary_engine import (
    ZoneBoundaryEngine,
)
from backend.models.base_region import BaseRegion
from backend.models.departure import Departure, DepartureDirection
from backend.models.pattern import PatternType
from backend.models.zone import ZoneType
from backend.models.zone_boundary import (
    BoundaryMode,
    BoundaryReasonCode,
    BoundarySet,
    ExceptionalBoundarySource,
)
from backend.validators.zone_boundary_validator import (
    BoundaryValidationError,
    ZoneBoundaryValidator,
)


def _frame(rows: list[tuple[float, float, float, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"])


def _departure(
    direction: DepartureDirection,
    *,
    leg_in_index: int = 0,
    leg_out_index: int = 3,
) -> Departure:
    return Departure(
        direction=direction,
        departure_index=leg_out_index,
        leg_in_direction=(
            DepartureDirection.BEARISH
            if direction == DepartureDirection.BULLISH
            else DepartureDirection.BULLISH
        ),
        leg_in_start_index=leg_in_index,
        leg_in_end_index=leg_in_index,
    )


@pytest.mark.parametrize(
    ("pattern", "direction", "expected_proximal", "expected_distal"),
    [
        (PatternType.DROP_BASE_RALLY, DepartureDirection.BULLISH, 102.0, 96.0),
        (PatternType.RALLY_BASE_RALLY, DepartureDirection.BULLISH, 102.0, 96.0),
        (PatternType.RALLY_BASE_DROP, DepartureDirection.BEARISH, 98.0, 104.0),
        (PatternType.DROP_BASE_DROP, DepartureDirection.BEARISH, 98.0, 104.0),
    ],
)
def test_body_to_wick_is_canonical_for_all_patterns(
    pattern: PatternType,
    direction: DepartureDirection,
    expected_proximal: float,
    expected_distal: float,
) -> None:
    leg_out = (
        (99, 110, 97, 108)
        if direction == DepartureDirection.BULLISH
        else (99, 103, 88, 90)
    )
    data = _frame(
        [
            (90, 95, 89, 94),
            (100, 103, 97, 102),
            (101, 104, 96, 98),
            leg_out,
        ]
    )
    result = ZoneBoundaryEngine().calculate(
        data,
        BaseRegion(1, 2),
        pattern,
        _departure(direction),
    )

    assert result.standard.mode == BoundaryMode.BODY_TO_WICK
    assert result.standard.proximal == expected_proximal
    assert result.standard.distal == expected_distal
    assert result.selected == result.standard


def test_wick_to_wick_is_stored_but_never_selected_silently() -> None:
    data = _frame(
        [(108, 109, 100, 101), (101, 106, 96, 103), (103, 112, 102, 111)]
    )
    result = ZoneBoundaryEngine().calculate(
        data,
        BaseRegion(1, 1),
        PatternType.DROP_BASE_RALLY,
        _departure(DepartureDirection.BULLISH, leg_out_index=2),
    )

    assert result.standard.proximal == 103.0
    assert result.wick_to_wick.proximal == 106.0
    assert result.wick_to_wick.distal == 96.0
    assert result.selected.mode == BoundaryMode.BODY_TO_WICK
    assert BoundaryReasonCode.ALTERNATE_WICK_TO_WICK in result.reason_codes


def test_dbr_can_use_overlapping_leg_in_as_exceptional_distal() -> None:
    data = _frame(
        [(105, 106, 88, 91), (92, 94, 90, 93), (93, 108, 92, 107)]
    )
    result = ZoneBoundaryEngine().calculate(
        data,
        BaseRegion(1, 1),
        PatternType.DROP_BASE_RALLY,
        _departure(DepartureDirection.BULLISH, leg_out_index=2),
    )

    assert result.standard.distal == 90.0
    assert result.exceptional is not None
    assert result.exceptional.distal == 88.0
    assert result.exceptional.exceptional_source == ExceptionalBoundarySource.LEG_IN
    assert result.selected == result.exceptional


def test_rbr_ignores_leg_in_and_can_use_leg_out_exception() -> None:
    data = _frame(
        [(90, 96, 88, 95), (96, 100, 92, 97), (97, 104, 90, 98)]
    )
    result = ZoneBoundaryEngine().calculate(
        data,
        BaseRegion(1, 1),
        PatternType.RALLY_BASE_RALLY,
        _departure(DepartureDirection.BULLISH, leg_out_index=2),
    )

    assert result.exceptional is not None
    assert result.exceptional.distal == 90.0
    assert result.exceptional.exceptional_source == ExceptionalBoundarySource.LEG_OUT


def test_rbd_can_use_leg_in_and_dbd_can_use_leg_out_exception() -> None:
    engine = ZoneBoundaryEngine()
    rbd = _frame(
        [(90, 112, 89, 108), (104, 110, 102, 105), (105, 108, 90, 91)]
    )
    rbd_result = engine.calculate(
        rbd,
        BaseRegion(1, 1),
        PatternType.RALLY_BASE_DROP,
        _departure(DepartureDirection.BEARISH, leg_out_index=2),
    )
    assert rbd_result.exceptional is not None
    assert rbd_result.exceptional.distal == 112.0
    assert (
        rbd_result.exceptional.exceptional_source
        == ExceptionalBoundarySource.LEG_IN
    )

    dbd = _frame(
        [(110, 111, 100, 101), (101, 108, 98, 100), (100, 110, 90, 91)]
    )
    dbd_result = engine.calculate(
        dbd,
        BaseRegion(1, 1),
        PatternType.DROP_BASE_DROP,
        _departure(DepartureDirection.BEARISH, leg_out_index=2),
    )
    assert dbd_result.exceptional is not None
    assert dbd_result.exceptional.distal == 110.0
    assert (
        dbd_result.exceptional.exceptional_source
        == ExceptionalBoundarySource.LEG_OUT
    )


@pytest.mark.parametrize(
    ("boundary", "reason"),
    [
        (
            BoundarySet(math.nan, 90, BoundaryMode.BODY_TO_WICK),
            BoundaryReasonCode.MALFORMED_BOUNDARY,
        ),
        (
            BoundarySet(0, 90, BoundaryMode.BODY_TO_WICK),
            BoundaryReasonCode.NON_POSITIVE_BOUNDARY,
        ),
        (
            BoundarySet(90, 90, BoundaryMode.BODY_TO_WICK),
            BoundaryReasonCode.ZERO_WIDTH_BOUNDARY,
        ),
        (
            BoundarySet(89, 90, BoundaryMode.BODY_TO_WICK),
            BoundaryReasonCode.INVERTED_BOUNDARY,
        ),
    ],
)
def test_boundary_validation_has_deterministic_reason_codes(
    boundary: BoundarySet, reason: BoundaryReasonCode
) -> None:
    with pytest.raises(BoundaryValidationError) as error:
        ZoneBoundaryValidator.validate(ZoneType.DEMAND, boundary)
    assert error.value.reason_code == reason
