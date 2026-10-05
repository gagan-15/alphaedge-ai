from __future__ import annotations

import pandas as pd

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
from backend.services.scanner.zone_lifecycle_ui_service import (
    ZoneLifecycleUiService,
)


def test_ui_service_exposes_canonical_lifecycle_and_authenticity_facts() -> None:
    data = pd.DataFrame(
        {
            "Open": [96, 97, 100, 102, 103, 104],
            "High": [98, 100, 103, 104, 105, 106],
            "Low": [95, 96, 99, 101, 102, 103],
            "Close": [97, 99, 102, 103, 104, 105],
        },
        index=pd.date_range("2026-01-01", periods=6, freq="D"),
    )
    zone = Zone(
        zone_type=ZoneType.DEMAND,
        upper_price=100,
        lower_price=95,
        created_index=1,
        pattern_type="DROP_BASE_RALLY",
    )

    metadata = ZoneLifecycleUiService().evaluate(
        [zone],
        data,
        symbol="TEST",
        timeframe="1D",
        current_price=105,
    )[1]

    assert metadata.lifecycle_status == "FRESH"
    assert metadata.authenticity_status == "AUTHENTIC"
    assert metadata.test_count == 0
    assert metadata.reaction_status == "NOT_REACTING"
    assert metadata.max_penetration_percent == 0


def test_ui_service_keeps_non_authentic_reason_explainable() -> None:
    data = pd.DataFrame(
        {
            "Open": [96, 97, 100, 102, 103, 104],
            "High": [98, 100, 103, 104, 105, 106],
            "Low": [95, 96, 99, 101, 102, 103],
            "Close": [97, 99, 102, 103, 104, 105],
        },
        index=pd.date_range("2026-01-01", periods=6, freq="D"),
    )
    zone = Zone(ZoneType.DEMAND, 100, 95, 1, pattern_type="DROP_BASE_RALLY")

    records = ZoneLifecycleUiService().evaluate(
        [zone, zone],
        data,
        symbol="TEST",
        timeframe="1D",
        current_price=105,
    )

    assert records[1].authenticity_reason_code in {"ORIGINAL", "DUPLICATE"}
    assert records[1].authenticity_reason


def _formation_candle(
    index: int,
    direction: CandleDirection,
    structure: CandleStructure,
) -> FormationCandleEvidence:
    return FormationCandleEvidence(
        index=index,
        timestamp=f"2026-08-{index + 3:02d}",
        classification=CandleClassification(
            index=index,
            direction=direction,
            structure=structure,
            body=10,
            candle_range=20,
            body_ratio=0.5,
            explosive=False,
        ),
    )


def test_sonacoms_like_immediate_visit_is_tested_and_dashboard_excluded() -> None:
    data = pd.DataFrame(
        {
            "Open": [775, 785, 790, 821.9, 790, 822.1],
            "High": [785, 794.45, 822.9, 824.6, 821, 836.9],
            "Low": [768.05, 774.5, 785.05, 786.25, 787, 807.6],
            "Close": [785, 787, 814.6, 792, 818.05, 812.5],
        },
        index=pd.to_datetime(
            [
                "2026-08-03",
                "2026-08-04",
                "2026-08-05",
                "2026-08-06",
                "2026-08-07",
                "2026-08-10",
            ]
        ),
    )
    leg_in = _formation_candle(0, CandleDirection.BULLISH, CandleStructure.EXCITING)
    base = _formation_candle(1, CandleDirection.BULLISH, CandleStructure.BASE)
    leg_out = _formation_candle(2, CandleDirection.BULLISH, CandleStructure.EXCITING)
    evidence = CanonicalFormationEvidence(
        pattern="RBR",
        leg_in_start_index=0,
        leg_in_end_index=0,
        leg_in_timestamps=(leg_in.timestamp,),
        leg_in_candles=(leg_in,),
        leg_in_direction=DepartureDirection.BULLISH,
        base_start_index=1,
        base_end_index=1,
        base_timestamps=(base.timestamp,),
        base_candles=(base,),
        base_body_ratios=(0.1,),
        base_candle_count=1,
        leg_out_start_index=2,
        leg_out_end_index=2,
        leg_out_timestamps=(leg_out.timestamp,),
        leg_out_candles=(leg_out,),
        first_leg_out_exciting=True,
        first_leg_out_explosive=False,
        second_leg_out_exciting=None,
        second_leg_out_explosive=None,
        significant_gap=False,
        gap_measurement=None,
        departure_strength=DepartureStrength.WEAK,
        closing_rule_passed=True,
        closing_comparison_reference=785,
        qualifying_close=814.6,
        acceptance_reason="ONE_EXCITING_LEG_OUT",
    )
    zone = Zone(
        zone_type=ZoneType.DEMAND,
        upper_price=787,
        lower_price=774.5,
        created_index=1,
        pattern_type="RALLY_BASE_RALLY",
        formation_evidence=evidence,
    )

    metadata = ZoneLifecycleUiService().evaluate(
        [zone],
        data,
        symbol="SONACOMS",
        timeframe="1D",
        current_price=812.5,
    )[1]

    assert metadata.lifecycle_status == "TESTED_RESPECTED"
    assert metadata.test_count == 1
    assert metadata.visit_count == 1
    assert not metadata.is_fresh
    assert metadata.reaction_status == "NOT_REACTING"
    assert not metadata.is_invalidated
    assert not metadata.dashboard_lifecycle_eligible
    assert metadata.dashboard_lifecycle_reason_code == "LIFECYCLE_TESTED"
