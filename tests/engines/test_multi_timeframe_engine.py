"""
Tests for the Multi-Timeframe Engine.
"""

from unittest.mock import Mock

import pandas as pd
import pytest

from backend.engines.multi_timeframe_engine.multi_timeframe_engine import (
    MultiTimeframeEngine,
)
from backend.models.market_structure.market_structure_result import (
    MarketStructureResult,
)
from backend.models.market_structure.market_structure_state import (
    StructureState,
    StructureTrend,
)
from backend.models.multi_timeframe.multi_timeframe_request import (
    MultiTimeframeRequest,
)


def _structure_result(
    trend: StructureTrend,
) -> MarketStructureResult:
    """
    Build a market structure result for one trend.
    """

    return MarketStructureResult(
        state=StructureState(
            trend=trend,
        ),
    )


def _request() -> MultiTimeframeRequest:
    """
    Build a two-timeframe request.
    """

    return MultiTimeframeRequest(
        primary_timeframe="1D",
        timeframes=["1D", "1H"],
    )


def _market_data() -> dict[str, pd.DataFrame]:
    """
    Build minimal data mapped by timeframe.
    """

    data = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [101.0],
            "Low": [99.0],
            "Close": [100.5],
        }
    )

    return {
        "1D": data.copy(),
        "1H": data.copy(),
    }


def test_all_bullish_timeframes_are_aligned() -> None:
    """
    Matching bullish timeframes produce bullish alignment.
    """

    engine = MultiTimeframeEngine()
    engine._market_structure = Mock()
    engine._market_structure.analyze.return_value = (
        _structure_result(
            StructureTrend.BULLISH,
        )
    )

    result = engine.analyze(
        _request(),
        _market_data(),
    )

    assert result.total_timeframes == 2
    assert result.primary_result is not None
    assert result.aligned_trend == StructureTrend.BULLISH
    assert result.is_aligned is True


def test_mixed_timeframes_are_not_aligned() -> None:
    """
    Mixed trends produce sideways alignment.
    """

    engine = MultiTimeframeEngine()
    engine._market_structure = Mock()
    engine._market_structure.analyze.side_effect = [
        _structure_result(
            StructureTrend.BULLISH,
        ),
        _structure_result(
            StructureTrend.BEARISH,
        ),
    ]

    result = engine.analyze(
        _request(),
        _market_data(),
    )

    assert result.aligned_trend == StructureTrend.SIDEWAYS
    assert result.is_aligned is False


def test_primary_timeframe_must_be_requested() -> None:
    """
    Invalid requests are rejected before analysis.
    """

    engine = MultiTimeframeEngine()

    with pytest.raises(ValueError):
        engine.analyze(
            MultiTimeframeRequest(
                primary_timeframe="1W",
                timeframes=["1D", "1H"],
            ),
            _market_data(),
        )
