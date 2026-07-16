"""
Tests for CHoCH Engine.

Sprint:
    2.30 - Change of Character Engine
"""

import pandas as pd
import pytest

from backend.config.choch_config import CHoCHConfig
from backend.engines.demand_supply_engine.choch_detector import (
    CHoCHDetector,
)
from backend.engines.demand_supply_engine.choch_engine import (
    CHoCHEngine,
)
from backend.models.bos_result import (
    BOSEvent,
    BOSDirection,
)
from backend.models.choch_result import CHoCHResult
from backend.models.structure_trend import StructureTrend
from backend.models.swing_point import (
    SwingPoint,
    SwingType,
)
from backend.validators.choch_validator import (
    CHoCHValidator,
)


@pytest.fixture
def valid_market_data():

    return pd.DataFrame(
        {
            "Open": [100, 101, 102, 103, 104, 105],
            "High": [101, 102, 103, 104, 105, 106],
            "Low": [99, 100, 101, 102, 103, 104],
            "Close": [100, 101, 102, 103, 104, 105],
        }
    )


@pytest.fixture
def swing_high():

    return SwingPoint(
        index=2,
        price=105.0,
        swing_type=SwingType.HIGH,
        confirmation_index=3,
    )


@pytest.fixture
def swing_low():

    return SwingPoint(
        index=3,
        price=95.0,
        swing_type=SwingType.LOW,
        confirmation_index=4,
    )


@pytest.fixture
def bullish_bos(swing_high):

    return BOSEvent(
        direction=BOSDirection.BULLISH,
        break_index=5,
        break_price=110.0,
        broken_swing=swing_high,
        break_distance=5.0,
        break_distance_percentage=4.76,
        confirmation_source="close",
        is_confirmed=True,
        explanation="Bullish BOS",
    )


@pytest.fixture
def bearish_bos(swing_low):

    return BOSEvent(
        direction=BOSDirection.BEARISH,
        break_index=5,
        break_price=90.0,
        broken_swing=swing_low,
        break_distance=5.0,
        break_distance_percentage=5.26,
        confirmation_source="close",
        is_confirmed=True,
        explanation="Bearish BOS",
    )


class TestCHoCHValidator:

    def test_valid_market_data(
        self,
        valid_market_data,
    ):

        CHoCHValidator.validate_market_data(
            valid_market_data,
        )

    def test_empty_dataframe(self):

        with pytest.raises(ValueError):

            CHoCHValidator.validate_market_data(
                pd.DataFrame(),
            )

    def test_invalid_type(self):

        with pytest.raises(TypeError):

            CHoCHValidator.validate_market_data(
                [],
            )

    def test_missing_columns(self):

        df = pd.DataFrame(
            {
                "Open": [1],
                "Close": [1],
            }
        )

        with pytest.raises(ValueError):

            CHoCHValidator.validate_market_data(df)

    def test_insufficient_rows(self):

        df = pd.DataFrame(
            {
                "Open": [1, 2],
                "High": [2, 3],
                "Low": [0, 1],
                "Close": [1, 2],
            }
        )

        with pytest.raises(ValueError):

            CHoCHValidator.validate_market_data(df)

    def test_default_config(self):

        config = CHoCHConfig()

        CHoCHValidator.validate_config(config)

    def test_negative_buffer(self):

        config = CHoCHConfig(
            break_buffer_value=-1,
        )

        with pytest.raises(ValueError):

            CHoCHValidator.validate_config(config)

    def test_invalid_confirmation_source(self):

        config = CHoCHConfig(
            confirmation_source="abc",
        )

        with pytest.raises(ValueError):

            CHoCHValidator.validate_config(config)

    def test_invalid_break_buffer_type(self):

        config = CHoCHConfig(
            break_buffer_type="xyz",
        )

        with pytest.raises(ValueError):

            CHoCHValidator.validate_config(config)

    def test_invalid_structure_points(self):

        config = CHoCHConfig(
            minimum_structure_points=1,
        )

        with pytest.raises(ValueError):

            CHoCHValidator.validate_config(config)


class TestCHoCHDetector:

    def test_bullish_choch_detected(
        self,
        bullish_bos,
    ):

        detector = CHoCHDetector()

        events = detector.detect(
            StructureTrend.BEARISH,
            [bullish_bos],
        )

        assert len(events) == 1
        assert events[0].direction == BOSDirection.BULLISH

    def test_bearish_choch_detected(
        self,
        bearish_bos,
    ):

        detector = CHoCHDetector()

        events = detector.detect(
            StructureTrend.BULLISH,
            [bearish_bos],
        )

        assert len(events) == 1
        assert events[0].direction == BOSDirection.BEARISH

    def test_no_choch_when_trend_matches(
        self,
        bullish_bos,
    ):

        detector = CHoCHDetector()

        events = detector.detect(
            StructureTrend.BULLISH,
            [bullish_bos],
        )

        assert events == []

    def test_sideways_returns_empty(
        self,
        bullish_bos,
        bearish_bos,
    ):

        detector = CHoCHDetector()

        events = detector.detect(
            StructureTrend.SIDEWAYS,
            [
                bullish_bos,
                bearish_bos,
            ],
        )

        assert events == []

    def test_empty_events(self):

        detector = CHoCHDetector()

        events = detector.detect(
            StructureTrend.BULLISH,
            [],
        )

        assert events == []


class TestCHoCHEngine:

    def test_engine_creation(self):

        engine = CHoCHEngine()

        assert engine is not None

    def test_engine_with_custom_config(self):

        config = CHoCHConfig()

        engine = CHoCHEngine(config)

        assert engine is not None

    def test_invalid_market_data(self):

        engine = CHoCHEngine()

        with pytest.raises(TypeError):

            engine.detect([])

    def test_empty_dataframe(self):

        engine = CHoCHEngine()

        with pytest.raises(ValueError):

            engine.detect(
                pd.DataFrame(),
            )

    def test_missing_columns(self):

        engine = CHoCHEngine()

        df = pd.DataFrame(
            {
                "Open": [1],
                "Close": [2],
            }
        )

        with pytest.raises(ValueError):

            engine.detect(df)

    def test_insufficient_rows(self):

        engine = CHoCHEngine()

        df = pd.DataFrame(
            {
                "Open": [1, 2],
                "High": [2, 3],
                "Low": [0, 1],
                "Close": [1, 2],
            }
        )

        with pytest.raises(ValueError):

            engine.detect(df)

    def test_returns_result_object(
        self,
        monkeypatch,
        valid_market_data,
        bullish_bos,
    ):

        engine = CHoCHEngine()

        swings = [
            SwingPoint(
                1,
                100,
                SwingType.HIGH,
                2,
            ),
            SwingPoint(
                2,
                90,
                SwingType.LOW,
                3,
            ),
            SwingPoint(
                3,
                105,
                SwingType.HIGH,
                4,
            ),
            SwingPoint(
                4,
                95,
                SwingType.LOW,
                5,
            ),
        ]

        monkeypatch.setattr(
            engine._swing_detector,
            "detect",
            lambda _: swings,
        )

        monkeypatch.setattr(
            engine._trend_resolver,
            "resolve",
            lambda _: StructureTrend.BEARISH,
        )

        monkeypatch.setattr(
            engine._bos_detector,
            "detect",
            lambda *_: [bullish_bos],
        )

        result = engine.detect(
            valid_market_data,
        )

        assert isinstance(
            result,
            CHoCHResult,
        )

        assert result.has_choch is True
        assert result.total_events == 1
        assert result.bullish_events == 1
        assert result.bearish_events == 0
        assert result.latest_event is not None
        assert result.latest_bullish_event is not None
        assert result.latest_bearish_event is None
        assert result.swings_evaluated == 4


class TestCHoCHIntegration:

    def test_no_bos_events(
        self,
        monkeypatch,
        valid_market_data,
    ):

        engine = CHoCHEngine()

        swings = [
            SwingPoint(
                1,
                100,
                SwingType.HIGH,
                2,
            ),
            SwingPoint(
                2,
                90,
                SwingType.LOW,
                3,
            ),
            SwingPoint(
                3,
                105,
                SwingType.HIGH,
                4,
            ),
            SwingPoint(
                4,
                95,
                SwingType.LOW,
                5,
            ),
        ]

        monkeypatch.setattr(
            engine._swing_detector,
            "detect",
            lambda _: swings,
        )

        monkeypatch.setattr(
            engine._trend_resolver,
            "resolve",
            lambda _: StructureTrend.BULLISH,
        )

        monkeypatch.setattr(
            engine._bos_detector,
            "detect",
            lambda *_: [],
        )

        result = engine.detect(
            valid_market_data,
        )

        assert result.has_choch is False
        assert result.total_events == 0
        assert result.latest_event is None
        assert result.latest_bullish_event is None
        assert result.latest_bearish_event is None

    def test_multiple_bullish_events(
        self,
        monkeypatch,
        valid_market_data,
        bullish_bos,
    ):

        engine = CHoCHEngine()

        swings = [
            SwingPoint(1, 100, SwingType.HIGH, 2),
            SwingPoint(2, 90, SwingType.LOW, 3),
            SwingPoint(3, 105, SwingType.HIGH, 4),
            SwingPoint(4, 95, SwingType.LOW, 5),
        ]

        monkeypatch.setattr(
            engine._swing_detector,
            "detect",
            lambda _: swings,
        )

        monkeypatch.setattr(
            engine._trend_resolver,
            "resolve",
            lambda _: StructureTrend.BEARISH,
        )

        monkeypatch.setattr(
            engine._bos_detector,
            "detect",
            lambda *_: [
                bullish_bos,
                bullish_bos,
            ],
        )

        result = engine.detect(
            valid_market_data,
        )

        assert result.has_choch
        assert result.bullish_events == 2
        assert result.total_events == 2

    def test_multiple_bearish_events(
        self,
        monkeypatch,
        valid_market_data,
        bearish_bos,
    ):

        engine = CHoCHEngine()

        swings = [
            SwingPoint(1, 100, SwingType.HIGH, 2),
            SwingPoint(2, 90, SwingType.LOW, 3),
            SwingPoint(3, 105, SwingType.HIGH, 4),
            SwingPoint(4, 95, SwingType.LOW, 5),
        ]

        monkeypatch.setattr(
            engine._swing_detector,
            "detect",
            lambda _: swings,
        )

        monkeypatch.setattr(
            engine._trend_resolver,
            "resolve",
            lambda _: StructureTrend.BULLISH,
        )

        monkeypatch.setattr(
            engine._bos_detector,
            "detect",
            lambda *_: [
                bearish_bos,
                bearish_bos,
            ],
        )

        result = engine.detect(
            valid_market_data,
        )

        assert result.has_choch
        assert result.bearish_events == 2
        assert result.total_events == 2

    def test_sideways_trend_has_no_choch(
        self,
        monkeypatch,
        valid_market_data,
        bullish_bos,
    ):

        engine = CHoCHEngine()

        swings = [
            SwingPoint(1, 100, SwingType.HIGH, 2),
            SwingPoint(2, 90, SwingType.LOW, 3),
            SwingPoint(3, 105, SwingType.HIGH, 4),
            SwingPoint(4, 95, SwingType.LOW, 5),
        ]

        monkeypatch.setattr(
            engine._swing_detector,
            "detect",
            lambda _: swings,
        )

        monkeypatch.setattr(
            engine._trend_resolver,
            "resolve",
            lambda _: StructureTrend.SIDEWAYS,
        )

        monkeypatch.setattr(
            engine._bos_detector,
            "detect",
            lambda *_: [bullish_bos],
        )

        result = engine.detect(
            valid_market_data,
        )

        assert result.has_choch is False
        assert result.total_events == 0

    def test_result_counts_are_consistent(
        self,
        monkeypatch,
        valid_market_data,
        bullish_bos,
    ):

        engine = CHoCHEngine()

        swings = [
            SwingPoint(1, 100, SwingType.HIGH, 2),
            SwingPoint(2, 90, SwingType.LOW, 3),
            SwingPoint(3, 105, SwingType.HIGH, 4),
            SwingPoint(4, 95, SwingType.LOW, 5),
        ]

        monkeypatch.setattr(
            engine._swing_detector,
            "detect",
            lambda _: swings,
        )

        monkeypatch.setattr(
            engine._trend_resolver,
            "resolve",
            lambda _: StructureTrend.BEARISH,
        )

        monkeypatch.setattr(
            engine._bos_detector,
            "detect",
            lambda *_: [bullish_bos],
        )

        result = engine.detect(
            valid_market_data,
        )

        assert result.total_events == (result.bullish_events + result.bearish_events)

        assert result.swings_evaluated == len(swings)
