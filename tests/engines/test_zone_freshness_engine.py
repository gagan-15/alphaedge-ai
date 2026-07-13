"""
Unit tests for ZoneFreshnessEngine.

Sprint:
    2.27 - Zone Freshness Engine
"""

import pandas as pd
import pytest

from backend.engines.demand_supply_engine.zone_freshness_engine import (
    ZoneFreshnessEngine,
)
from backend.models.zone import Zone, ZoneType
from backend.models.zone_freshness_result import FreshnessStatus


class TestZoneFreshnessEngine:
    """
    Tests for ZoneFreshnessEngine.
    """

    def setup_method(self) -> None:
        self.engine = ZoneFreshnessEngine()

    def test_fresh_zone(self) -> None:
        """
        Zone should remain fresh when price never revisits it.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 120, 121],
                "High": [110, 122, 123],
                "Low": [100, 118, 119],
                "Close": [108, 121, 122],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.status == FreshnessStatus.FRESH
        assert result.touch_count == 0

    def test_zone_with_one_touch(self) -> None:
        """
        Zone should report one touch after a single retest.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 108, 120],
                "High": [110, 109, 122],
                "Low": [100, 105, 118],
                "Close": [108, 107, 121],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.touch_count == 1

    def test_multiple_consecutive_candles_count_as_one_touch(self) -> None:
        """
        Consecutive candles inside the zone
        should count as one touch.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 108, 107, 106, 120],
                "High": [110, 109, 108, 107, 122],
                "Low": [100, 105, 104, 103, 118],
                "Close": [108, 107, 106, 105, 121],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.touch_count == 1

    def test_penetration_percentage(self) -> None:
        """
        Penetration percentage should be greater
        than zero when price enters the zone.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 108],
                "High": [110, 109],
                "Low": [100, 104],
                "Close": [108, 107],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.penetration_percent > 0

    def test_no_penetration(self) -> None:
        """
        Penetration should be zero when price
        never enters the zone.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [120, 121],
                "High": [122, 123],
                "Low": [118, 119],
                "Close": [121, 122],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.penetration_percent == 0.0

    def test_invalid_zone_raises_error(self) -> None:
        """
        Invalid zone should raise ValueError.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=100.0,
            lower_price=110.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [101],
                "Low": [99],
                "Close": [100],
            }
        )

        with pytest.raises(ValueError):
            self.engine.evaluate(
                zone,
                market_data,
            )

    def test_weak_zone_status(self) -> None:
        """
        Deep penetration should mark the zone as weak.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 108],
                "High": [110, 109],
                "Low": [102, 101],
                "Close": [108, 102],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.status == FreshnessStatus.WEAK

    def test_broken_zone_status(self) -> None:
        """
        Full penetration should mark the zone as broken.
        """

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 108],
                "High": [110, 109],
                "Low": [100, 95],
                "Close": [108, 96],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.status == FreshnessStatus.BROKEN
        assert result.is_broken is True

    def test_supply_zone_penetration(self) -> None:
        """
        Penetration should be calculated correctly
        for a supply zone.
        """

        zone = Zone(
            zone_type=ZoneType.SUPPLY,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 106],
                "High": [110, 108],
                "Low": [100, 102],
                "Close": [105, 107],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.penetration_percent > 0
