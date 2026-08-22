import pandas as pd

from backend.models.zone import Zone, ZoneType
from backend.services.scanner.stock_details_analysis_service import (
    StockDetailsAnalysisService,
)


def test_aligned_benchmark_returns_use_matching_dates() -> None:
    dates = pd.date_range("2025-01-01", periods=140, freq="B")
    stock = pd.Series(range(100, 240), index=dates, dtype=float)
    benchmark = pd.Series(range(100, 170), index=dates[::2], dtype=float)

    result = StockDetailsAnalysisService._returns(stock, benchmark)

    assert result["1m"]["status"] in {"OUTPERFORMING", "MATCHING", "UNDERPERFORMING"}
    assert "difference" in result["1m"]
    assert result["6m"]["status"] == "INSUFFICIENT_HISTORY"


def test_selected_zone_must_exist_in_current_canonical_detection() -> None:
    service = StockDetailsAnalysisService()
    canonical = Zone(ZoneType.DEMAND, 239.80, 236.00, 10)

    selected = service._select_canonical_zone(
        [canonical], "DEMAND", 239.80, 236.00
    )

    assert selected is canonical


def test_rejected_legacy_zone_cannot_be_reconstructed_from_request_prices() -> None:
    service = StockDetailsAnalysisService()

    try:
        service._select_canonical_zone([], "DEMAND", 720.50, 707.00)
    except LookupError as error:
        assert "current canonical methodology" in str(error)
    else:
        raise AssertionError("A non-canonical requested zone was accepted")
