"""
Tests for Multi-Timeframe Engine.

Sprint:
    2.32 - Multi-Timeframe Engine
"""

import pandas as pd
import pytest

from backend.engines.multi_timeframe_engine.multi_timeframe_engine import (
    MultiTimeframeEngine,
)
from backend.models.multi_timeframe.multi_timeframe_request import (
    MultiTimeframeRequest,
)
from backend.models.multi_timeframe.multi_timeframe_result import (
    MultiTimeframeResult,
)


@pytest.fixture
def sample_market_data():

    df = pd.DataFrame(
        {
            "Open": [100, 101, 102, 103, 104, 105, 106],
            "High": [101, 103, 105, 104, 107, 106, 108],
            "Low": [99, 100, 101, 100, 103, 102, 104],
            "Close": [100, 102, 104, 103, 106, 105, 107],
        }
    )

    return {
        "1W": df.copy(),
        "1D": df.copy(),
        "4H": df.copy(),
        "1H": df.copy(),
    }


@pytest.fixture
def request():

    return MultiTimeframeRequest(
        primary_timeframe="1D",
        timeframes=[
            "1W",
            "1D",
            "4H",
            "1H",
        ],
    )


class TestMultiTimeframeEngine:

    def test_engine_creation(self):

        engine = MultiTimeframeEngine()

        assert engine is not None

    def test_result_type(
        self,
        request,
        sample_market_data,
    ):

        engine = MultiTimeframeEngine()

        result = engine.analyze(
            request,
            sample_market_data,
        )

        assert isinstance(
            result,
            MultiTimeframeResult,
        )

    def test_primary_timeframe(
        self,
        request,
        sample_market_data,
    ):

        engine = MultiTimeframeEngine()

        result = engine.analyze(
            request,
            sample_market_data,
        )

        assert result.primary_timeframe == "1D"

    def test_total_timeframes(
        self,
        request,
        sample_market_data,
    ):

        engine = MultiTimeframeEngine()

        result = engine.analyze(
            request,
            sample_market_data,
        )

        assert result.total_timeframes == 4

    def test_primary_result(
        self,
        request,
        sample_market_data,
    ):

        engine = MultiTimeframeEngine()

        result = engine.analyze(
            request,
            sample_market_data,
        )

        assert result.primary_result is not None
