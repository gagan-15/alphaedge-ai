from dataclasses import asdict

import numpy as np
import pandas as pd

from backend.engines.demand_supply_engine.zone_detection_engine import ZoneDetectionEngine
from backend.services.market_data.incremental_canonical_service import (
    IncrementalCanonicalService,
)


def _candles(size: int = 240) -> pd.DataFrame:
    random = np.random.default_rng(8127)
    close = 100 + np.cumsum(random.normal(0, 1.1, size))
    open_ = close + random.normal(0, 0.8, size)
    high = np.maximum(open_, close) + random.uniform(0.2, 1.8, size)
    low = np.minimum(open_, close) - random.uniform(0.2, 1.8, size)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close,
         "Volume": random.integers(1000, 10000, size)},
        index=pd.date_range("2025-01-01", periods=size, freq="B"),
    )


def _payloads(zones):
    return [asdict(zone) for zone in zones]


def test_append_only_incremental_formation_matches_full_reference() -> None:
    data = _candles()
    prior = ZoneDetectionEngine().detect_zones(data.iloc[:-1])
    actual = IncrementalCanonicalService().refresh(
        data, _payloads(prior), len(data) - 1,
    ).zones
    expected = ZoneDetectionEngine().detect_zones(data)

    assert _payloads(actual) == _payloads(expected)


def test_revised_candle_incremental_formation_matches_full_reference() -> None:
    original = _candles()
    prior = ZoneDetectionEngine().detect_zones(original)
    revised = original.copy()
    position = len(revised) - 8
    revised.iloc[position, revised.columns.get_loc("Close")] = (
        revised.iloc[position]["Open"] + 0.1
    )
    expected = ZoneDetectionEngine().detect_zones(revised)
    actual = IncrementalCanonicalService().refresh(
        revised, _payloads(prior), position,
    ).zones

    assert _payloads(actual) == _payloads(expected)
