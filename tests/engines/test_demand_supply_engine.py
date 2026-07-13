"""
Unit tests for DemandSupplyEngine.

Sprint:
    2.25 - Demand & Supply Foundation
"""

import pytest
import pandas as pd

from backend.engines.demand_supply_engine.demand_supply_engine import (
    DemandSupplyEngine,
)
from backend.models.zone import Zone, ZoneType


class TestDemandSupplyEngine:
    """
    Tests for DemandSupplyEngine.
    """

    def setup_method(self) -> None:
        """
        Create engine for each test.
        """
        self.engine = DemandSupplyEngine()

    def test_validate_valid_zone(self) -> None:
        """
        Valid zone should be returned unchanged.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=250.0,
            lower_price=240.0,
        )

        result = self.engine.validate(zone)

        assert result == zone

    def test_validate_invalid_upper_price(self) -> None:
        """
        Upper price must be greater than zero.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=0.0,
            lower_price=240.0,
        )

        with pytest.raises(ValueError):
            self.engine.validate(zone)

    def test_validate_invalid_lower_price(self) -> None:
        """
        Lower price must be greater than zero.
        """

        zone = Zone(
            zone_type=ZoneType.SUPPLY,
            upper_price=250.0,
            lower_price=0.0,
        )

        with pytest.raises(ValueError):
            self.engine.validate(zone)

    def test_validate_invalid_price_range(self) -> None:
        """
        Upper price must be greater than lower price.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=240.0,
            lower_price=250.0,
        )

        with pytest.raises(ValueError):
            self.engine.validate(zone)

    def test_prepare_data_returns_copy(self) -> None:
        """
        prepare_data should return a copy
        of the DataFrame.
        """

        market_data = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [95.0],
                "Close": [102.0],
                "Volume": [1000],
            }
        )

        result = self.engine.prepare_data(market_data)

        assert result.equals(market_data)
        assert result is not market_data

    def test_prepare_data_does_not_modify_original(self) -> None:
        """
        prepare_data should not modify
        the original DataFrame.
        """

        market_data = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [95.0],
                "Close": [102.0],
                "Volume": [1000],
            }
        )

        result = self.engine.prepare_data(market_data)

        result.loc[0, "Close"] = 999.0

        assert market_data.loc[0, "Close"] == 102.0
