"""
Tests for the Scanner API response mapping.
"""

from pandas import DataFrame

from backend.api.scanner import _measure_zone, build_scanner_response
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
