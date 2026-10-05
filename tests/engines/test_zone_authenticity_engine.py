"""Milestone 3 tests for canonical zone authenticity."""

from __future__ import annotations

import pandas as pd
import pytest

from backend.engines.demand_supply_engine.zone_authenticity_engine import (
    ZoneAuthenticityEngine,
)
from backend.models.zone import Zone, ZoneType
from backend.models.zone_authenticity import (
    AuthenticityReasonCode,
    AuthenticityStatus,
    FormationEvidence,
    ReactionSource,
    ZoneRelationshipType,
)


def _market_data() -> pd.DataFrame:
    return pd.DataFrame(
        [
            (90, 110, 89, 105),
            (105, 108, 100, 102),
            (102, 115, 101, 114),
            (114, 116, 104, 106),
            (106, 112, 103, 110),
            (110, 111, 98, 99),
        ],
        columns=["Open", "High", "Low", "Close"],
        index=pd.date_range("2026-01-01", periods=6, freq="D"),
    )


def _zone(
    upper: float,
    lower: float,
    index: int,
    *,
    zone_type: ZoneType = ZoneType.DEMAND,
    pattern: str = "DROP_BASE_RALLY",
    active: bool = True,
) -> Zone:
    return Zone(
        zone_type=zone_type,
        upper_price=upper,
        lower_price=lower,
        created_index=index,
        pattern_type=pattern,
        is_fresh=active,
    )


def test_original_zone_is_authentic() -> None:
    result = ZoneAuthenticityEngine().classify(
        [_zone(105, 100, 1)],
        _market_data(),
        symbol="TCS",
        timeframe="1D",
    )

    assert len(result) == 1
    assert result[0].status == AuthenticityStatus.AUTHENTIC
    assert result[0].reason_code == AuthenticityReasonCode.ORIGINAL
    assert result[0].parent_zone_id is None


def test_reaction_zone_records_parent_depth_time_and_source() -> None:
    parent = _zone(108, 100, 1)
    reaction = _zone(107, 104, 3)
    result = ZoneAuthenticityEngine().classify(
        [parent, reaction],
        _market_data(),
        symbol="TCS",
        timeframe="1D",
    )

    first, second = result
    assert second.status == AuthenticityStatus.NON_AUTHENTIC
    assert second.reason_code == AuthenticityReasonCode.REACTION
    assert second.parent_zone_id == first.zone_id
    assert second.reaction_depth_percent == 50.0
    assert second.reaction_timestamp == "2026-01-04T00:00:00"
    assert second.reaction_source == ReactionSource.BODY
    assert second.zone_id in first.child_zone_ids


def test_wick_only_reaction_is_distinguished() -> None:
    data = _market_data()
    data.iloc[3] = (111, 112, 107, 110)
    result = ZoneAuthenticityEngine().classify(
        [_zone(108, 100, 1), _zone(110, 107, 3)],
        data,
        symbol="TCS",
        timeframe="1D",
    )

    assert result[1].reason_code == AuthenticityReasonCode.REACTION
    assert result[1].reaction_source == ReactionSource.WICK
    assert result[1].reaction_depth_percent == 12.5


def test_duplicate_uses_tick_normalized_canonical_identity() -> None:
    original = _zone(105.001, 100.001, 1)
    duplicate = _zone(105.002, 100.002, 1)
    result = ZoneAuthenticityEngine().classify(
        [original, duplicate],
        _market_data(),
        symbol="TCS",
        timeframe="1D",
        tick_size=0.05,
    )

    assert result[0].zone_id == result[1].zone_id
    assert result[0].occurrence_id != result[1].occurrence_id
    assert result[1].reason_code == AuthenticityReasonCode.DUPLICATE
    assert result[1].duplicate_of_zone_id == result[0].zone_id


def test_nested_zones_are_linked_but_not_merged() -> None:
    parent = _zone(110, 100, 1, active=False)
    child = _zone(108, 103, 3)
    result = ZoneAuthenticityEngine().classify(
        [parent, child],
        _market_data(),
        symbol="TCS",
        timeframe="1D",
        active_zone_indexes={3},
    )

    assert len(result) == 2
    assert result[1].reason_code == AuthenticityReasonCode.NESTED
    assert result[1].parent_zone_id == result[0].zone_id
    assert result[1].zone_id in result[0].child_zone_ids
    assert any(
        relation.relationship_type == ZoneRelationshipType.NESTED_PARENT
        for relation in result[1].relationships
    )


def test_partial_overlap_is_recorded_without_merging_or_invalidation() -> None:
    earlier = _zone(106, 100, 1, active=False)
    later = _zone(110, 104, 3)
    result = ZoneAuthenticityEngine().classify(
        [earlier, later],
        _market_data(),
        symbol="TCS",
        timeframe="1D",
        active_zone_indexes={3},
    )

    assert len(result) == 2
    assert result[1].reason_code == AuthenticityReasonCode.OVERLAPPING
    relationship = next(
        relation
        for relation in result[1].relationships
        if relation.relationship_type == ZoneRelationshipType.OVERLAPPING
    )
    assert relationship.related_zone_id == result[0].zone_id
    assert relationship.overlap_percent == pytest.approx(33.3333)


@pytest.mark.parametrize(
    ("zone_type", "close", "expected"),
    [
        (ZoneType.DEMAND, 121.0, True),
        (ZoneType.DEMAND, 110.0, False),
        (ZoneType.SUPPLY, 80.0, True),
        (ZoneType.SUPPLY, 91.0, False),
    ],
)
def test_good_closing_uses_complete_leg_in_extreme(
    zone_type: ZoneType, close: float, expected: bool
) -> None:
    data = _market_data()
    data.iloc[0] = (100, 112, 90, 105)
    data.iloc[1] = (105, 120, 95, 115)
    data.iloc[3] = (100, max(121, close), min(80, close), close)
    zone = _zone(
        108,
        100,
        2,
        zone_type=zone_type,
        pattern=(
            "DROP_BASE_RALLY"
            if zone_type == ZoneType.DEMAND
            else "RALLY_BASE_DROP"
        ),
    )
    result = ZoneAuthenticityEngine().classify(
        [zone],
        data,
        symbol="TCS",
        timeframe="1D",
        formation_evidence={2: FormationEvidence(0, 1, 3)},
    )

    assert result[0].good_closing is expected


def test_good_closing_does_not_make_reaction_zone_authentic() -> None:
    data = _market_data()
    data.iloc[4] = (106, 121, 103, 120)
    result = ZoneAuthenticityEngine().classify(
        [_zone(108, 100, 1), _zone(107, 103, 3)],
        data,
        symbol="TCS",
        timeframe="1D",
        formation_evidence={3: FormationEvidence(2, 2, 4)},
    )

    assert result[1].good_closing is True
    assert result[1].status == AuthenticityStatus.NON_AUTHENTIC
    assert result[1].reason_code == AuthenticityReasonCode.REACTION


def test_identity_changes_with_symbol_timeframe_pattern_or_origin() -> None:
    engine = ZoneAuthenticityEngine()
    data = _market_data()
    zone = _zone(105, 100, 1)
    tcs_daily = engine.classify(
        [zone], data, symbol="TCS", timeframe="1D"
    )[0]
    infy_daily = engine.classify(
        [zone], data, symbol="INFY", timeframe="1D"
    )[0]
    tcs_weekly = engine.classify(
        [zone], data, symbol="TCS", timeframe="1W"
    )[0]
    other_origin = engine.classify(
        [_zone(105, 100, 2)], data, symbol="TCS", timeframe="1D"
    )[0]

    assert len(
        {
            tcs_daily.zone_id,
            infy_daily.zone_id,
            tcs_weekly.zone_id,
            other_origin.zone_id,
        }
    ) == 4


def test_invalid_context_is_rejected_deterministically() -> None:
    with pytest.raises(ValueError, match="tick_size"):
        ZoneAuthenticityEngine().classify(
            [_zone(105, 100, 1)],
            _market_data(),
            symbol="TCS",
            timeframe="1D",
            tick_size=0,
        )


def test_frozen_authenticity_comparison_corpus() -> None:
    engine = ZoneAuthenticityEngine()
    data = _market_data()
    reaction_data = _market_data()
    reaction_data.iloc[4] = (106, 121, 103, 120)
    scenarios = [
        engine.classify(
            [_zone(105, 100, 1)], data, symbol="ORIGINAL", timeframe="1D"
        ),
        engine.classify(
            [_zone(108, 100, 1), _zone(107, 104, 3)],
            reaction_data,
            symbol="REACTION",
            timeframe="1D",
            formation_evidence={3: FormationEvidence(2, 2, 4)},
        ),
        engine.classify(
            [_zone(105.001, 100.001, 1), _zone(105.002, 100.002, 1)],
            data,
            symbol="DUPLICATE",
            timeframe="1D",
        ),
        engine.classify(
            [_zone(110, 100, 1, active=False), _zone(108, 103, 3)],
            data,
            symbol="NESTED",
            timeframe="1D",
            active_zone_indexes={3},
        ),
        engine.classify(
            [_zone(106, 100, 1, active=False), _zone(110, 104, 3)],
            data,
            symbol="OVERLAP",
            timeframe="1D",
            active_zone_indexes={3},
        ),
    ]
    records = [record for scenario in scenarios for record in scenario]

    assert len(records) == 9
    assert sum(
        record.status == AuthenticityStatus.AUTHENTIC for record in records
    ) == 5
    assert sum(
        record.status == AuthenticityStatus.NON_AUTHENTIC for record in records
    ) == 4
    assert {
        reason: sum(record.reason_code == reason for record in records)
        for reason in AuthenticityReasonCode
    } == {
        AuthenticityReasonCode.ORIGINAL: 5,
        AuthenticityReasonCode.REACTION: 1,
        AuthenticityReasonCode.DUPLICATE: 1,
        AuthenticityReasonCode.NESTED: 1,
        AuthenticityReasonCode.OVERLAPPING: 1,
    }
    assert sum(record.good_closing is True for record in records) == 1
