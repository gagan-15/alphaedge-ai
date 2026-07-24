"""
Tests for the Scanner API response mapping.
"""

from backend.api.scanner import (
    build_scanner_response,
    get_scanner,
)
from backend.models.market_scanner.market_scanner_result import (
    MarketScannerResult,
)
from backend.models.screener.screener_result import (
    ScreenerResult,
)


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


def test_get_scanner_returns_valid_response() -> None:
    """
    Scanner API function returns controlled sample results.
    """

    response = get_scanner()

    assert response.total_scanned == 4
    assert response.total_matches == 2
    assert len(response.results) == 2
    assert response.results[0].symbol == "INFY"
    assert response.results[0].approved is True
    assert response.results[0].confirmed is True
