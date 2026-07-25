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
