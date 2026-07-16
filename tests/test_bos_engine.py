"""
Unit tests for BOSEngine.

Sprint:
    2.29 - Break of Structure Engine
"""

import pandas as pd
import pytest

from backend.config.bos_config import BOSConfig
from backend.engines.demand_supply_engine.bos_engine import BOSEngine
from backend.models.bos_result import BOSDirection

from backend.engines.demand_supply_engine.bos_detector import BOSDetector
from backend.models.swing_point import SwingPoint, SwingType


class TestBOSEngine:

    def setup_method(self) -> None:
        self.engine = BOSEngine()

    @staticmethod
    def _bullish_market_data() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Open": [
                    98,
                    102,
                    106,
                    104,
                    102,
                    108,
                    112,
                ],
                "High": [
                    100,
                    106,
                    110,
                    107,
                    105,
                    111,
                    116,
                ],
                "Low": [
                    96,
                    100,
                    104,
                    101,
                    99,
                    106,
                    110,
                ],
                "Close": [
                    99,
                    104,
                    108,
                    103,
                    101,
                    109,
                    115,
                ],
            }
        )

    @staticmethod
    def _bearish_market_data() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Open": [
                    112,
                    108,
                    104,
                    106,
                    108,
                    101,
                    96,
                ],
                "High": [
                    114,
                    110,
                    106,
                    108,
                    110,
                    103,
                    98,
                ],
                "Low": [
                    110,
                    106,
                    100,
                    103,
                    105,
                    99,
                    94,
                ],
                "Close": [
                    111,
                    107,
                    102,
                    105,
                    107,
                    100,
                    95,
                ],
            }
        )

    def test_bullish_bos_detected(self) -> None:

        market_data = self._bullish_market_data()

        result = self.engine.detect(
            market_data,
        )

        assert result.has_bullish_bos is True

    def test_bullish_event_direction(self) -> None:

        market_data = self._bullish_market_data()

        result = self.engine.detect(
            market_data,
        )

        assert result.latest_bullish_event.direction == BOSDirection.BULLISH

    def test_bearish_bos_detected(self) -> None:

        market_data = self._bearish_market_data()

        result = self.engine.detect(
            market_data,
        )

        assert result.has_bearish_bos is True

    def test_bearish_event_direction(self) -> None:

        market_data = self._bearish_market_data()

        result = self.engine.detect(
            market_data,
        )

        assert result.latest_bearish_event.direction == BOSDirection.BEARISH

    def test_no_bos_detected(self) -> None:

        market_data = pd.DataFrame(
            {
                "Open": [
                    100,
                    102,
                    104,
                    102,
                    100,
                    101,
                    102,
                ],
                "High": [
                    102,
                    106,
                    110,
                    106,
                    104,
                    105,
                    106,
                ],
                "Low": [
                    98,
                    100,
                    102,
                    99,
                    97,
                    98,
                    99,
                ],
                "Close": [
                    101,
                    104,
                    108,
                    103,
                    99,
                    102,
                    103,
                ],
            }
        )

        result = self.engine.detect(
            market_data,
        )

        assert result.has_bos is False

    def test_latest_event_is_returned(self) -> None:

        market_data = self._bullish_market_data()

        result = self.engine.detect(
            market_data,
        )

        assert result.latest_event is not None

    def test_swings_evaluated_is_positive(self) -> None:

        market_data = self._bullish_market_data()

        result = self.engine.detect(
            market_data,
        )

        assert result.swings_evaluated > 0

    def test_bullish_event_count(self) -> None:

        market_data = self._bullish_market_data()

        result = self.engine.detect(
            market_data,
        )

        assert result.bullish_events == 1

    def test_bearish_event_count(self) -> None:

        market_data = self._bearish_market_data()

        result = self.engine.detect(
            market_data,
        )

        assert result.bearish_events == 1

    def test_empty_market_data_raises_value_error(self) -> None:

        market_data = pd.DataFrame()

        with pytest.raises(
            ValueError,
            match="market_data cannot be empty",
        ):
            self.engine.detect(
                market_data,
            )

    def test_invalid_market_data_type_raises_type_error(self) -> None:

        with pytest.raises(
            TypeError,
            match="market_data must be a pandas DataFrame",
        ):
            self.engine.detect(
                [],
            )

    def test_missing_required_column_raises_value_error(self) -> None:

        market_data = pd.DataFrame(
            {
                "Open": [100, 101, 102, 103, 104],
                "High": [102, 103, 104, 105, 106],
                "Low": [98, 99, 100, 101, 102],
            }
        )

        with pytest.raises(
            ValueError,
            match="Missing required columns",
        ):
            self.engine.detect(
                market_data,
            )

    def test_insufficient_market_data_raises_value_error(self) -> None:

        market_data = pd.DataFrame(
            {
                "Open": [100, 101, 102],
                "High": [102, 103, 104],
                "Low": [98, 99, 100],
                "Close": [101, 102, 103],
            }
        )

        with pytest.raises(
            ValueError,
            match="Insufficient market data",
        ):
            self.engine.detect(
                market_data,
            )

    def test_invalid_left_swing_bars_raises_value_error(self) -> None:

        config = BOSConfig(
            swing_left_bars=0,
        )

        engine = BOSEngine(
            config,
        )

        market_data = self._bullish_market_data()

        with pytest.raises(
            ValueError,
            match="swing_left_bars must be greater than zero",
        ):
            engine.detect(
                market_data,
            )

    def test_invalid_right_swing_bars_raises_value_error(self) -> None:

        config = BOSConfig(
            swing_right_bars=0,
        )

        engine = BOSEngine(
            config,
        )

        market_data = self._bullish_market_data()

        with pytest.raises(
            ValueError,
            match="swing_right_bars must be greater than zero",
        ):
            engine.detect(
                market_data,
            )

    def test_negative_break_buffer_raises_value_error(self) -> None:

        config = BOSConfig(
            break_buffer_value=-1.0,
        )

        engine = BOSEngine(
            config,
        )

        with pytest.raises(
            ValueError,
            match="break_buffer_value cannot be negative",
        ):
            engine.detect(
                self._bullish_market_data(),
            )

    def test_equal_bullish_break_not_allowed_by_default(self) -> None:

        config = BOSConfig(
            allow_equal_break=False,
        )

        detector = BOSDetector(
            config,
        )

        assert (
            detector._is_bullish_break(
                110.0,
                110.0,
            )
            is False
        )

    def test_equal_bullish_break_allowed(self) -> None:

        config = BOSConfig(
            allow_equal_break=True,
        )

        detector = BOSDetector(
            config,
        )

        assert (
            detector._is_bullish_break(
                110.0,
                110.0,
            )
            is True
        )

    def test_equal_bearish_break_not_allowed_by_default(self) -> None:

        config = BOSConfig(
            allow_equal_break=False,
        )

        detector = BOSDetector(
            config,
        )

        assert (
            detector._is_bearish_break(
                100.0,
                100.0,
            )
            is False
        )

    def test_equal_bearish_break_allowed(self) -> None:

        config = BOSConfig(
            allow_equal_break=True,
        )

        detector = BOSDetector(
            config,
        )

        assert (
            detector._is_bearish_break(
                100.0,
                100.0,
            )
            is True
        )

    def test_percentage_buffer_for_bullish_break(self) -> None:

        config = BOSConfig(
            break_buffer_type="percentage",
            break_buffer_value=5.0,
        )

        detector = BOSDetector(
            config,
        )

        assert (
            detector._is_bullish_break(
                106.0,
                100.0,
            )
            is True
        )

    def test_percentage_buffer_rejects_small_bullish_break(self) -> None:

        config = BOSConfig(
            break_buffer_type="percentage",
            break_buffer_value=5.0,
        )

        detector = BOSDetector(
            config,
        )

        assert (
            detector._is_bullish_break(
                104.0,
                100.0,
            )
            is False
        )

    def test_percentage_buffer_for_bearish_break(self) -> None:

        config = BOSConfig(
            break_buffer_type="percentage",
            break_buffer_value=5.0,
        )

        detector = BOSDetector(
            config,
        )

        assert (
            detector._is_bearish_break(
                94.0,
                100.0,
            )
            is True
        )

    def test_points_buffer_for_bullish_break(self) -> None:

        config = BOSConfig(
            break_buffer_type="points",
            break_buffer_value=5.0,
        )

        detector = BOSDetector(
            config,
        )

        assert (
            detector._is_bullish_break(
                106.0,
                100.0,
            )
            is True
        )

    def test_points_buffer_for_bearish_break(self) -> None:

        config = BOSConfig(
            break_buffer_type="points",
            break_buffer_value=5.0,
        )

        detector = BOSDetector(
            config,
        )

        assert (
            detector._is_bearish_break(
                94.0,
                100.0,
            )
            is True
        )

    def test_invalid_break_buffer_type_raises_value_error(self) -> None:

        config = BOSConfig(
            break_buffer_type="invalid",
        )

        detector = BOSDetector(
            config,
        )

        with pytest.raises(
            ValueError,
            match="Unsupported break_buffer_type",
        ):
            detector._apply_break_buffer(
                100.0,
                bullish=True,
            )

    def test_close_confirmation_source(self) -> None:

        config = BOSConfig(
            confirmation_source="close",
        )

        detector = BOSDetector(
            config,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [95],
                "Close": [105],
            }
        )

        price = detector._get_confirmation_price(
            market_data,
            0,
            SwingType.HIGH,
        )

        assert price == 105.0

    def test_high_confirmation_source(self) -> None:

        config = BOSConfig(
            confirmation_source="high",
        )

        detector = BOSDetector(
            config,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [95],
                "Close": [105],
            }
        )

        price = detector._get_confirmation_price(
            market_data,
            0,
            SwingType.HIGH,
        )

        assert price == 110.0

    def test_low_confirmation_source(self) -> None:

        config = BOSConfig(
            confirmation_source="low",
        )

        detector = BOSDetector(
            config,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [95],
                "Close": [105],
            }
        )

        price = detector._get_confirmation_price(
            market_data,
            0,
            SwingType.LOW,
        )

        assert price == 95.0

    def test_invalid_confirmation_source_raises_value_error(self) -> None:

        config = BOSConfig(
            confirmation_source="invalid",
        )

        detector = BOSDetector(
            config,
        )

        market_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [95],
                "Close": [105],
            }
        )

        with pytest.raises(
            ValueError,
            match="Unsupported confirmation_source",
        ):
            detector._get_confirmation_price(
                market_data,
                0,
                SwingType.HIGH,
            )

    def test_bos_event_contains_break_distance(self) -> None:

        config = BOSConfig()

        detector = BOSDetector(
            config,
        )

        swing = SwingPoint(
            index=2,
            price=110.0,
            swing_type=SwingType.HIGH,
            confirmation_index=4,
        )

        event = detector._create_event(
            BOSDirection.BULLISH,
            swing,
            break_index=6,
            break_price=115.0,
        )

        assert event.break_distance == 5.0

    def test_bos_event_contains_break_percentage(self) -> None:

        config = BOSConfig()

        detector = BOSDetector(
            config,
        )

        swing = SwingPoint(
            index=2,
            price=100.0,
            swing_type=SwingType.HIGH,
            confirmation_index=4,
        )

        event = detector._create_event(
            BOSDirection.BULLISH,
            swing,
            break_index=6,
            break_price=105.0,
        )

        assert event.break_distance_percentage == 5.0

    def test_bos_event_is_confirmed(self) -> None:

        config = BOSConfig()

        detector = BOSDetector(
            config,
        )

        swing = SwingPoint(
            index=2,
            price=100.0,
            swing_type=SwingType.HIGH,
            confirmation_index=4,
        )

        event = detector._create_event(
            BOSDirection.BULLISH,
            swing,
            break_index=6,
            break_price=105.0,
        )

        assert event.is_confirmed is True

    def test_bos_event_contains_explanation(self) -> None:

        config = BOSConfig()

        detector = BOSDetector(
            config,
        )

        swing = SwingPoint(
            index=2,
            price=100.0,
            swing_type=SwingType.HIGH,
            confirmation_index=4,
        )

        event = detector._create_event(
            BOSDirection.BULLISH,
            swing,
            break_index=6,
            break_price=105.0,
        )

        assert "BULLISH BOS" in event.explanation

    def test_market_data_is_not_modified(self) -> None:

        market_data = self._bullish_market_data()

        original = market_data.copy(
            deep=True,
        )

        self.engine.detect(
            market_data,
        )

        pd.testing.assert_frame_equal(
            market_data,
            original,
        )
