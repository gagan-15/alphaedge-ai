"""
Unit tests for ZoneStrengthEngine.

Sprint:
    2.28 - Zone Strength Engine
"""

import pandas as pd

from backend.engines.demand_supply_engine.zone_strength_engine import (
    ZoneStrengthEngine,
)
from backend.models.zone import Zone, ZoneType
from backend.models.zone_strength_result import StrengthStatus


class TestZoneStrengthEngine:

    def setup_method(self) -> None:
        self.engine = ZoneStrengthEngine()

    def test_default_strength(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [99],
                "Close": [109],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.status == StrengthStatus.WEAK

    def test_departure_distance_defaults_to_zero(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [99],
                "Close": [109],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.departure_distance == 0.0

    def test_departure_speed_defaults_to_zero(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [99],
                "Close": [109],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.departure_speed == 0.0

    def test_volume_confirmation_defaults_to_false(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [99],
                "Close": [109],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.volume_confirmed is False

    def test_gap_presence_defaults_to_false(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [99],
                "Close": [109],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.gap_present is False

    def test_departure_distance_is_positive(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 111],
                "High": [110, 130],
                "Low": [100, 109],
                "Close": [109, 128],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.departure_distance > 0

    def test_departure_candle_count(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 111, 115, 118],
                "High": [110, 116, 120, 121],
                "Low": [100, 110, 114, 117],
                "Close": [109, 115, 119, 116],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.departure_candle_count == 2

    def test_departure_speed_is_positive(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 111, 115],
                "High": [110, 120, 130],
                "Low": [100, 110, 114],
                "Close": [109, 119, 129],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.departure_speed > 0

    def test_gap_present_for_demand_zone(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 115],
                "High": [110, 120],
                "Low": [100, 114],
                "Close": [109, 118],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.gap_present is True

    def test_volume_confirmation_is_true(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100, 110],
                "High": [110, 120],
                "Low": [99, 109],
                "Close": [109, 118],
                "Volume": [1000, 5000],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.volume_confirmed is True

    def test_strength_status_moderate(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 111],
                "High": [110, 125],
                "Low": [100, 110],
                "Close": [109, 124],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.status == StrengthStatus.MODERATE

    def test_strength_status_strong(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 111],
                "High": [110, 145],
                "Low": [100, 110],
                "Close": [109, 144],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.status == StrengthStatus.STRONG

    def test_strength_status_very_strong(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 111],
                "High": [110, 170],
                "Low": [100, 110],
                "Close": [109, 169],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.status == StrengthStatus.VERY_STRONG

    def test_volume_confirmation_without_volume_column(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100, 110],
                "High": [110, 120],
                "Low": [99, 109],
                "Close": [109, 118],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.volume_confirmed is False

    def test_volume_confirmation_single_candle(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [99],
                "Close": [109],
                "Volume": [1000],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.volume_confirmed is False

    def test_gap_not_present_for_demand_zone(self) -> None:

        zone = Zone(
            zone_type=ZoneType.DEMAND,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 108],
                "High": [110, 115],
                "Low": [100, 107],
                "Close": [109, 114],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.gap_present is False

    def test_gap_present_for_supply_zone(self) -> None:

        zone = Zone(
            zone_type=ZoneType.SUPPLY,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 95],
                "High": [110, 99],
                "Low": [100, 90],
                "Close": [101, 92],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.gap_present is True

    def test_gap_not_present_for_supply_zone(self) -> None:

        zone = Zone(
            zone_type=ZoneType.SUPPLY,
            upper_price=110.0,
            lower_price=100.0,
            created_index=0,
        )

        market_data = pd.DataFrame(
            {
                "Open": [105, 102],
                "High": [110, 108],
                "Low": [100, 98],
                "Close": [101, 99],
            }
        )

        result = self.engine.evaluate(
            zone,
            market_data,
        )

        assert result.gap_present is False
