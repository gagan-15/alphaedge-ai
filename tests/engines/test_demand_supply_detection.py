"""
Tests for Demand and Supply zone detection.
"""

import pandas as pd

from backend.engines.demand_supply_engine.demand_supply_engine import (
    DemandSupplyEngine,
)
from backend.models.zone import (
    ZoneType,
)


def test_detects_fresh_demand_zone() -> None:
    """
    A valid base and bullish departure create a demand zone.
    """

    market_data = pd.DataFrame(
        {
            "Open": [
                90.0,
                90.0,
                100.0,
                101.0,
                110.0,
                112.0,
            ],
            "High": [
                92.0,
                101.0,
                102.0,
                103.5,
                112.0,
                114.0,
            ],
            "Low": [
                89.0,
                89.0,
                99.0,
                101.0,
                109.0,
                111.0,
            ],
            "Close": [
                91.0,
                100.0,
                101.0,
                103.0,
                111.0,
                113.0,
            ],
            "Volume": [
                1000,
                1500,
                900,
                1800,
                1700,
                1600,
            ],
        }
    )

    zones = DemandSupplyEngine().detect(
        market_data,
    )

    assert len(zones) >= 1
    assert zones[0].zone_type == ZoneType.DEMAND
    assert zones[0].is_fresh is True
    assert zones[0].touch_count == 0


def test_returns_no_zones_without_departure() -> None:
    """
    Flat candles do not create a zone.
    """

    market_data = pd.DataFrame(
        {
            "Open": [100.0] * 6,
            "High": [101.0] * 6,
            "Low": [99.0] * 6,
            "Close": [100.5] * 6,
            "Volume": [1000] * 6,
        }
    )

    zones = DemandSupplyEngine().detect(
        market_data,
    )

    assert zones == []
