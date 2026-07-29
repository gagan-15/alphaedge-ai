import pandas as pd

from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.api.scanner import _is_zone_invalidated
from backend.models.zone import Zone, ZoneType


def _candidate_data(
    leg_in_open: float, leg_in_close: float, bullish: bool = True, strong: bool = True
) -> pd.DataFrame:
    if bullish:
        departure_close = 114.0 if strong else 109.0
        closes = [leg_in_close, 106.2, departure_close, 118.0, 121.0]
        opens = [leg_in_open, 106.0, 106.5, departure_close, 118.0]
        highs = [
            max(leg_in_open, leg_in_close) + 1,
            107.0,
            departure_close + 1,
            119.0,
            122.0,
        ]
        lows = [
            min(leg_in_open, leg_in_close) - 1,
            105.0,
            106.0,
            departure_close - 1,
            117.0,
        ]
    else:
        departure_close = 96.0 if strong else 101.0
        closes = [leg_in_close, 104.8, departure_close, 92.0, 89.0]
        opens = [leg_in_open, 105.0, 104.5, departure_close, 92.0]
        highs = [
            max(leg_in_open, leg_in_close) + 1,
            106.0,
            105.0,
            departure_close + 1,
            93.0,
        ]
        lows = [
            min(leg_in_open, leg_in_close) - 1,
            104.0,
            departure_close - 1,
            91.0,
            88.0,
        ]
    return pd.DataFrame(
        {"Open": opens, "High": highs, "Low": lows, "Close": closes},
        index=pd.date_range("2026-01-01", periods=5),
    )


def _formed(diagnostics: list[dict[str, object]]) -> list[dict[str, object]]:
    return [item for item in diagnostics if item["zone_type"] is not None]


def test_diagnostics_preserve_accepted_rbr_output() -> None:
    data = _candidate_data(100.0, 105.0)
    engine = ZoneDetectionEngine()

    production = engine.detect_zones(data)
    diagnostic_zones, diagnostics = engine.detect_zones_with_diagnostics(data)

    assert diagnostic_zones == production
    assert any(
        item["status"] == "accepted" and item["pattern"] == "RALLY_BASE_RALLY"
        for item in diagnostics
    )


def test_diagnostics_capture_rejected_rbr() -> None:
    data = _candidate_data(100.0, 105.0, strong=False)

    _, diagnostics = ZoneDetectionEngine().detect_zones_with_diagnostics(data)
    rejected = [item for item in _formed(diagnostics) if item["status"] == "rejected"]

    assert any(item["pattern"] == "RALLY_BASE_RALLY" for item in rejected)
    assert any(item["rejection_reasons"] for item in rejected)


def test_diagnostics_capture_accepted_dbr() -> None:
    data = _candidate_data(110.0, 105.0)

    _, diagnostics = ZoneDetectionEngine().detect_zones_with_diagnostics(data)

    assert any(
        item["status"] == "accepted" and item["pattern"] == "DROP_BASE_RALLY"
        for item in diagnostics
    )


def test_diagnostics_capture_rejected_supply_candidate() -> None:
    data = _candidate_data(100.0, 105.0, bullish=False, strong=False)

    _, diagnostics = ZoneDetectionEngine().detect_zones_with_diagnostics(data)

    assert any(
        item["status"] == "rejected" and item["zone_type"] == "SUPPLY"
        for item in diagnostics
    )


def test_diagnostics_capture_candidate_not_formed() -> None:
    data = _candidate_data(100.0, 105.0)

    _, diagnostics = ZoneDetectionEngine().detect_zones_with_diagnostics(data)

    assert any(
        item["zone_type"] is None
        and "Candidate not formed" in item["rejection_reasons"][0]
        for item in diagnostics
    )


def test_existing_invalidation_rule_identifies_breached_zone() -> None:
    data = pd.DataFrame(
        {
            "Open": [105.0, 104.0, 99.0],
            "High": [106.0, 105.0, 100.0],
            "Low": [103.0, 102.0, 95.0],
            "Close": [104.0, 103.0, 96.0],
        }
    )
    zone = Zone(
        zone_type=ZoneType.DEMAND,
        upper_price=104.0,
        lower_price=100.0,
        created_index=0,
    )

    assert _is_zone_invalidated(zone, data) is True
