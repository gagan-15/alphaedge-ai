import pandas as pd

from backend.engines.demand_supply_engine.departure_detector import DepartureDetector
from backend.models.base_region import BaseRegion


def _data(leg_in_close: float, departure_close: float, final_close: float) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [100.0, 110.0, 110.5, 111.0, departure_close, final_close - 1],
            "High": [leg_in_close + 1, 111.0, 111.0, departure_close + 1, final_close + 1, final_close + 1],
            "Low": [99.0, 109.5, 110.0, 110.5, departure_close - 1, final_close - 2],
            "Close": [leg_in_close, 110.5, 110.7, departure_close, final_close, final_close],
        }
    )


def test_leg_out_must_exceed_leg_in_for_any_pattern() -> None:
    data = _data(110.0, 118.0, 119.0)
    base = BaseRegion(start_index=1, end_index=2)

    assert DepartureDetector().detect(data, base) is None


def test_strong_leg_out_with_follow_through_is_allowed() -> None:
    data = _data(105.0, 118.0, 124.0)
    base = BaseRegion(start_index=1, end_index=2)

    assert DepartureDetector().detect(data, base) is not None


def test_overlapping_non_explosive_leg_out_is_rejected() -> None:
    data = pd.DataFrame(
        {
            "Open": [100.0, 105.0, 106.0, 107.0, 109.0, 108.5],
            "High": [106.0, 108.0, 108.0, 110.0, 110.0, 110.0],
            "Low": [99.0, 104.0, 105.0, 106.5, 107.0, 107.5],
            "Close": [105.0, 106.0, 106.5, 109.0, 108.5, 109.5],
        }
    )
    base = BaseRegion(start_index=1, end_index=2)

    assert DepartureDetector().detect(data, base) is None


def test_gap_up_can_form_bullish_departure_with_follow_through() -> None:
    data = pd.DataFrame(
        {
            "Open": [100.0, 104.0, 104.5, 111.0, 113.0, 116.0],
            "High": [105.0, 105.0, 105.0, 113.0, 116.0, 119.0],
            "Low": [99.0, 103.5, 104.0, 110.0, 112.0, 115.0],
            "Close": [104.0, 104.5, 104.6, 112.0, 115.0, 118.0],
        }
    )
    base = BaseRegion(start_index=1, end_index=2)

    departure = DepartureDetector().detect(data, base)

    assert departure is not None
    assert departure.direction.value == "BULLISH"


def test_gap_down_can_form_bearish_departure_with_follow_through() -> None:
    data = pd.DataFrame(
        {
            "Open": [110.0, 106.0, 105.5, 98.0, 96.0, 93.0],
            "High": [111.0, 107.0, 106.0, 99.0, 97.0, 94.0],
            "Low": [105.0, 105.0, 105.0, 96.0, 93.0, 90.0],
            "Close": [106.0, 105.5, 105.4, 97.0, 94.0, 91.0],
        }
    )
    base = BaseRegion(start_index=1, end_index=2)

    departure = DepartureDetector().detect(data, base)

    assert departure is not None
    assert departure.direction.value == "BEARISH"
