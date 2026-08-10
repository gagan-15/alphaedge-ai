from backend.models.candle_classification import (
    CandleClassification,
    CandleDirection,
    CandleStructure,
)
from backend.models.departure import DepartureDirection, DepartureStrength
from backend.models.formation_evidence import (
    CanonicalFormationEvidence,
    FormationCandleEvidence,
)
from backend.models.zone import Zone, ZoneType
from backend.services.scanner.dashboard_zone_qualification_service import (
    DashboardZoneQualificationService,
)


def _candle(
    index,
    structure,
    direction,
    body,
    *,
    explosive=False,
    relative=1.6,
    close=0.1,
    body_ratio=0.75,
):
    classification = CandleClassification(
        index=index,
        direction=direction,
        structure=structure,
        body=body,
        candle_range=body / body_ratio,
        body_ratio=body_ratio,
        explosive=explosive,
        range_to_median=relative,
        close_location=close,
    )
    return FormationCandleEvidence(index, f"2026-01-{index + 1:02d}", classification)


def _zone(
    *,
    base_count=1,
    outgoing=None,
    qualifying_close=115,
    gap=False,
    legacy=0,
    incoming_body=8,
):
    bases = tuple(
        _candle(i + 1, CandleStructure.BASE, CandleDirection.NEUTRAL, 1)
        for i in range(base_count)
    )
    legs = outgoing or (
        _candle(
            base_count + 1,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            15,
            explosive=True,
        ),
    )
    incoming = (
        _candle(
            0,
            CandleStructure.EXCITING,
            CandleDirection.BEARISH,
            incoming_body,
        ),
    )
    evidence = CanonicalFormationEvidence(
        pattern="DBR",
        leg_in_start_index=0,
        leg_in_end_index=0,
        leg_in_timestamps=(incoming[0].timestamp,),
        leg_in_candles=incoming,
        leg_in_direction=DepartureDirection.BEARISH,
        base_start_index=1,
        base_end_index=base_count,
        base_timestamps=tuple(x.timestamp for x in bases),
        base_candles=bases,
        base_body_ratios=tuple(0.25 for _ in bases),
        base_candle_count=base_count,
        leg_out_start_index=base_count + 1,
        leg_out_end_index=base_count + len(legs),
        leg_out_timestamps=tuple(x.timestamp for x in legs),
        leg_out_candles=legs,
        first_leg_out_exciting=True,
        first_leg_out_explosive=legs[0].classification.explosive,
        second_leg_out_exciting=len(legs) > 1,
        second_leg_out_explosive=(
            legs[1].classification.explosive if len(legs) > 1 else None
        ),
        significant_gap=gap,
        gap_measurement=0.4 if gap else None,
        departure_strength=DepartureStrength.STRONG,
        closing_rule_passed=True,
        closing_comparison_reference=109,
        qualifying_close=qualifying_close,
        acceptance_reason="Canonical test formation.",
    )
    return Zone(
        ZoneType.DEMAND,
        110,
        100,
        1,
        strength=legacy,
        pattern_type="DROP_BASE_RALLY",
        formation_evidence=evidence,
    )


def test_explosive_departure_qualifies_with_or_without_gap():
    service = DashboardZoneQualificationService()
    assert service.qualify(_zone()).dashboard_qualified
    with_gap = service.qualify(_zone(gap=True))
    assert (
        with_gap.dashboard_qualified
        and "GAP_PRESENT" in with_gap.qualification_reason_codes
    )


def test_two_aligned_exciting_candles_qualify():
    legs = tuple(
        _candle(
            i,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            8,
            explosive=False,
            relative=1.2,
            close=0.2,
        )
        for i in (2, 3)
    )
    assert (
        DashboardZoneQualificationService()
        .qualify(_zone(outgoing=legs, qualifying_close=116))
        .dashboard_qualified
    )


def test_strong_single_non_explosive_exciting_departure_can_qualify():
    legs = (
        _candle(2, CandleStructure.EXCITING, CandleDirection.BULLISH, 16,
                explosive=False, relative=2.0, close=0.25, body_ratio=0.65),
    )
    result = DashboardZoneQualificationService().qualify(
        _zone(outgoing=legs, qualifying_close=121)
    )
    assert result.dashboard_qualified
    assert result.departure_quality == "ACCEPTABLE"
    assert "STRONG_SINGLE_EXCITING_DEPARTURE" in result.qualification_reason_codes


def test_weak_single_exciting_departure_is_rejected():
    legs = (
        _candle(2, CandleStructure.EXCITING, CandleDirection.BULLISH, 8,
                explosive=False, relative=1.1, close=0.35),
    )
    result = DashboardZoneQualificationService().qualify(
        _zone(outgoing=legs, qualifying_close=112)
    )
    assert not result.dashboard_qualified
    assert result.departure_quality == "WEAK"


def test_honaut_like_two_base_decisive_single_exciting_departure_qualifies():
    legs = (
        _candle(3, CandleStructure.EXCITING, CandleDirection.BULLISH, 2575,
                explosive=False, relative=5.5076577, close=0.3462017,
                body_ratio=0.6413449564),
    )
    original = _zone(
        base_count=2,
        outgoing=legs,
        qualifying_close=40105,
        incoming_body=560,
    )
    zone = Zone(
        ZoneType.DEMAND, 37650, 37205, original.created_index,
        pattern_type=original.pattern_type,
        formation_evidence=original.formation_evidence,
    )
    result = DashboardZoneQualificationService().qualify(zone)
    assert result.dashboard_qualified
    assert result.departure_quality == "ACCEPTABLE"
    assert result.leg_out_body_ratio == 0.641345
    assert result.leg_out_range_to_median == 5.507658
    assert result.directional_close_distance == 0.346202
    assert result.departure_zone_width_ratio == 5.516854
    assert result.leg_out_to_leg_in_body_ratio == 4.598214


def test_weak_stair_step_is_rejected():
    legs = tuple(
        _candle(
            i,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            3,
            explosive=False,
            relative=0.7,
            close=0.3,
        )
        for i in (2, 3, 4)
    )
    result = DashboardZoneQualificationService().qualify(
        _zone(outgoing=legs, qualifying_close=111)
    )
    assert (
        not result.dashboard_qualified
        and "WEAK_DEPARTURE" in result.qualification_reason_codes
    )


def test_wick_heavy_poor_close_is_rejected():
    legs = (
        _candle(
            2,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            12,
            explosive=False,
            close=0.7,
        ),
    )
    result = DashboardZoneQualificationService().qualify(_zone(outgoing=legs))
    assert (
        not result.dashboard_qualified
        and "POOR_DIRECTIONAL_CLOSE" in result.qualification_reason_codes
    )


def test_one_two_and_three_candle_compact_bases_qualify():
    service = DashboardZoneQualificationService()
    results = [service.qualify(_zone(base_count=count)) for count in (1, 2, 3)]
    assert all(result.dashboard_qualified for result in results)
    assert [result.base_compactness for result in results] == [
        "EXCELLENT",
        "STRONG",
        "ACCEPTABLE",
    ]
    assert [result.base_preference_rank for result in results] == [0, 1, 2]


def test_long_base_is_rejected():
    result = DashboardZoneQualificationService().qualify(_zone(base_count=4))
    assert (
        not result.dashboard_qualified
        and "BASE_TOO_LONG_FOR_PRIMARY_DASHBOARD"
        in result.qualification_reason_codes
    )
    assert result.base_candle_count == 4
    assert result.base_compactness == "NOT_PRIMARY"


def test_five_candle_base_is_rejected_even_with_explosive_departure():
    zone = _zone(base_count=5)
    evidence_before = zone.formation_evidence
    result = DashboardZoneQualificationService().qualify(zone)
    assert not result.dashboard_qualified
    assert result.base_compactness == "NOT_PRIMARY"
    assert "BASE_TOO_LONG_FOR_PRIMARY_DASHBOARD" in result.qualification_reason_codes
    assert zone.formation_evidence is evidence_before
    assert zone.upper_price == 110
    assert zone.lower_price == 100


def test_compact_base_never_rescues_weak_departure():
    legs = (
        _candle(
            2,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            5,
            explosive=False,
            relative=0.8,
            close=0.3,
        ),
    )
    service = DashboardZoneQualificationService()
    for count, expected in ((1, "EXCELLENT"), (2, "STRONG"), (3, "ACCEPTABLE")):
        result = service.qualify(
            _zone(base_count=count, outgoing=legs, qualifying_close=111)
        )
        assert not result.dashboard_qualified
        assert result.base_compactness == expected
        assert "WEAK_DEPARTURE" in result.qualification_reason_codes


def test_one_base_acceptable_single_departure_is_excellent_compactness():
    legs = (
        _candle(
            2,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            16,
            explosive=False,
            relative=2.0,
            close=0.25,
            body_ratio=0.65,
        ),
    )
    result = DashboardZoneQualificationService().qualify(
        _zone(base_count=1, outgoing=legs, qualifying_close=121)
    )
    assert result.dashboard_qualified
    assert result.departure_quality == "ACCEPTABLE"
    assert result.base_compactness == "EXCELLENT"


def test_legacy_quality_cannot_override_weak_evidence():
    legs = (
        _candle(
            2,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            5,
            explosive=False,
            relative=0.8,
            close=0.3,
        ),
    )
    assert (
        not DashboardZoneQualificationService()
        .qualify(_zone(outgoing=legs, qualifying_close=111, legacy=85))
        .dashboard_qualified
    )


def test_htf_context_is_not_part_of_qualification_input():
    zone = _zone()
    service = DashboardZoneQualificationService()
    assert service.qualify(zone) == service.qualify(zone)


def test_daily_one_base_explosive_zone_is_dashboard_eligible():
    result = DashboardZoneQualificationService().qualify(
        _zone(base_count=1), "1D"
    )
    assert result.dashboard_qualified
    assert result.departure_quality == "EXPLOSIVE"


def test_daily_multi_base_zones_remain_canonical_but_are_dashboard_rejected():
    service = DashboardZoneQualificationService()
    for count in (2, 3):
        zone = _zone(base_count=count)
        evidence = zone.formation_evidence
        result = service.qualify(zone, "1D")
        assert not result.dashboard_qualified
        assert "MULTI_BASE_EXECUTION_ZONE" in result.qualification_reason_codes
        assert zone.formation_evidence is evidence
        assert zone.upper_price == 110 and zone.lower_price == 100


def test_125_minute_single_base_strong_single_qualifies():
    legs = (
        _candle(
            2,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            16,
            explosive=False,
            relative=2.0,
            close=0.25,
            body_ratio=0.65,
        ),
    )
    result = DashboardZoneQualificationService().qualify(
        _zone(base_count=1, outgoing=legs, qualifying_close=121), "125M"
    )
    assert result.dashboard_qualified
    assert result.departure_quality == "ACCEPTABLE"


def test_125_minute_two_base_explosive_zone_is_dashboard_rejected():
    result = DashboardZoneQualificationService().qualify(
        _zone(base_count=2), "125M"
    )
    assert not result.dashboard_qualified
    assert "MULTI_BASE_EXECUTION_ZONE" in result.qualification_reason_codes


def test_weekly_single_base_strong_multi_candle_zone_qualifies():
    legs = tuple(
        _candle(
            index,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            8,
            explosive=False,
            relative=1.2,
            close=0.2,
        )
        for index in (2, 3)
    )
    result = DashboardZoneQualificationService().qualify(
        _zone(base_count=1, outgoing=legs, qualifying_close=116), "1W"
    )
    assert result.dashboard_qualified
    assert result.departure_quality == "STRONG"


def test_weekly_two_base_explosive_zone_is_dashboard_rejected():
    result = DashboardZoneQualificationService().qualify(
        _zone(base_count=2), "1W"
    )
    assert not result.dashboard_qualified
    assert "MULTI_BASE_EXECUTION_ZONE" in result.qualification_reason_codes


def test_monthly_two_base_zone_preserves_existing_dashboard_behavior():
    result = DashboardZoneQualificationService().qualify(
        _zone(base_count=2), "1M"
    )
    assert result.dashboard_qualified
    assert "MULTI_BASE_EXECUTION_ZONE" not in result.qualification_reason_codes


def test_daily_single_base_weak_departure_still_fails_departure_gate():
    legs = (
        _candle(
            2,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            5,
            explosive=False,
            relative=0.8,
            close=0.3,
        ),
    )
    result = DashboardZoneQualificationService().qualify(
        _zone(base_count=1, outgoing=legs, qualifying_close=111), "1D"
    )
    assert not result.dashboard_qualified
    assert "WEAK_DEPARTURE" in result.qualification_reason_codes


def test_daily_single_base_strong_single_failing_volatility_is_rejected():
    legs = (
        _candle(
            2,
            CandleStructure.EXCITING,
            CandleDirection.BULLISH,
            16,
            explosive=False,
            relative=1.49,
            close=0.25,
            body_ratio=0.65,
        ),
    )
    result = DashboardZoneQualificationService().qualify(
        _zone(base_count=1, outgoing=legs, qualifying_close=121), "1D"
    )
    assert not result.dashboard_qualified
    assert result.departure_quality == "WEAK"
