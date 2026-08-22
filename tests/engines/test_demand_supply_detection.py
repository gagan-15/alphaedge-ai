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
                116.0,
                118.0,
            ],
            "High": [
                92.0,
                101.0,
                102.0,
                115.0,
                118.0,
                120.0,
            ],
            "Low": [
                89.0,
                89.0,
                99.0,
                101.0,
                115.0,
                117.0,
            ],
            "Close": [
                91.0,
                100.0,
                101.0,
                114.0,
                117.0,
                119.0,
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


def test_rejects_zone_when_leg_out_is_weaker_than_leg_in() -> None:
    """A large incoming leg followed by a smaller exit is not a strong zone."""

    market_data = pd.DataFrame(
        {
            "Open": [80.0, 100.0, 101.0, 101.2, 103.0, 104.0],
            "High": [101.0, 102.0, 101.8, 103.0, 104.0, 105.0],
            "Low": [79.0, 99.0, 100.8, 101.0, 102.0, 103.0],
            "Close": [100.0, 101.0, 101.2, 102.8, 103.5, 104.5],
            "Volume": [1000, 900, 850, 1200, 1100, 1000],
        }
    )

    zones = DemandSupplyEngine().detect(market_data)

    assert zones == []
