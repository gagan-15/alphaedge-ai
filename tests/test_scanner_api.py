"""
Tests for the Scanner API response mapping.
"""

from pandas import DataFrame, date_range

from backend.api.scanner import (
    _is_zone_invalidated,
    _measure_zone,
    _timeframe_data,
    build_scanner_response,
)
from backend.models.market_scanner.market_scanner_result import (
    MarketScannerResult,
)
from backend.models.screener.screener_result import (
    ScreenerResult,
)
from backend.models.zone import Zone, ZoneType


def test_build_empty_scanner_response() -> None:
    """
    Empty scanner results map to a valid API response.
    """

    scanner = MarketScannerResult(
        scanned_symbols=4,
        screener_result=ScreenerResult(
            opportunities=[],
        ),
    )

    response = build_scanner_response(scanner)

    assert response.total_scanned == 4
    assert response.total_matches == 0
    assert response.results == ()


def test_measure_zone_uses_departure_and_later_retests() -> None:
    """Zone quality inputs must come from observable candles."""

    data = DataFrame(
        [
            {"Open": 100, "High": 102, "Low": 99, "Close": 101},
            {"Open": 101, "High": 103, "Low": 100, "Close": 102},
            {"Open": 102, "High": 108, "Low": 102, "Close": 107},
            {"Open": 107, "High": 112, "Low": 106, "Close": 111},
            {"Open": 111, "High": 114, "Low": 109, "Close": 113},
            {"Open": 113, "High": 115, "Low": 101, "Close": 104},
        ]
    )
    measured = _measure_zone(
        Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=103,
            lower_price=100,
            created_index=1,
        ),
        data,
    )

    assert measured.strength > 0
    assert measured.touch_count == 1
    assert measured.is_fresh is False


def test_timeframe_data_aggregates_daily_candles() -> None:
    """Weekly zones must use true aggregated OHLCV candles."""

    data = DataFrame(
        {
            "Open": [100, 101, 102, 103, 104],
            "High": [102, 103, 104, 105, 106],
            "Low": [99, 100, 101, 102, 103],
            "Close": [101, 102, 103, 104, 105],
            "Volume": [10, 20, 30, 40, 50],
        },
        index=date_range("2026-07-20", periods=5, freq="D"),
    )

    weekly = _timeframe_data(data, "WEEKLY")

    assert len(weekly) == 1
    assert weekly.iloc[0]["Open"] == 100
    assert weekly.iloc[0]["High"] == 106
    assert weekly.iloc[0]["Low"] == 99
    assert weekly.iloc[0]["Close"] == 105
    assert weekly.iloc[0]["Volume"] == 150


def test_measure_zone_penalizes_departure_without_follow_through() -> None:
    """A short move followed by immediate reversal must not score as explosive."""

    data = DataFrame(
        [
            {"Open": 100, "High": 103, "Low": 99, "Close": 102},
            {"Open": 102, "High": 103, "Low": 100, "Close": 101},
            {"Open": 101, "High": 110, "Low": 101, "Close": 108},
            {"Open": 108, "High": 109, "Low": 99, "Close": 100},
            {"Open": 100, "High": 102, "Low": 96, "Close": 98},
        ]
    )
    measured = _measure_zone(
        Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=103,
            lower_price=100,
            created_index=1,
        ),
        data,
    )

    assert measured.strength < 10


def test_demand_zone_is_invalid_after_close_below_distal() -> None:
    data = DataFrame(
        [
            {"Open": 101, "High": 103, "Low": 100, "Close": 102},
            {"Open": 102, "High": 106, "Low": 101, "Close": 105},
            {"Open": 105, "High": 106, "Low": 99, "Close": 100},
            {"Open": 100, "High": 101, "Low": 96, "Close": 97},
        ]
    )
    zone = Zone(
        zone_type=ZoneType.DEMAND,
        upper_price=102,
        lower_price=98,
        created_index=0,
    )

    assert _is_zone_invalidated(zone, data) is True


def test_supply_zone_is_invalid_after_close_above_distal() -> None:
    data = DataFrame(
        [
            {"Open": 101, "High": 103, "Low": 100, "Close": 102},
            {"Open": 102, "High": 103, "Low": 95, "Close": 96},
            {"Open": 96, "High": 103, "Low": 95, "Close": 102},
            {"Open": 102, "High": 106, "Low": 101, "Close": 105},
        ]
    )
    zone = Zone(
        zone_type=ZoneType.SUPPLY,
        upper_price=104,
        lower_price=100,
        created_index=0,
    )

    assert _is_zone_invalidated(zone, data) is True
