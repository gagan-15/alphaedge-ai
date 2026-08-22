from datetime import datetime
from math import atan, degrees
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from backend.engines.trend_engine.canonical_trend_engine import (
    CanonicalTrendEngine,
)
from backend.models.canonical_trend import (
    CanonicalTrendState,
    SmaColour,
    TrendAlignment,
    TrendReasonCode,
)

IST = ZoneInfo("Asia/Kolkata")


def candles(
    closes: list[float],
    *,
    start: str = "2026-01-01",
    frequency: str = "D",
) -> pd.DataFrame:
    close = pd.Series(closes, dtype="float64")
    return pd.DataFrame(
        {
            "Open": close.to_numpy(),
            "High": (close + 1.0).to_numpy(),
            "Low": (close - 1.0).to_numpy(),
            "Close": close.to_numpy(),
            "Volume": 1_000.0,
        },
        index=pd.date_range(start, periods=len(close), freq=frequency),
    )


def test_sma50_and_t_minus_seven_use_exact_windows() -> None:
    engine = CanonicalTrendEngine()
    data = candles([float(value) for value in range(1, 61)])

    result = engine.evaluate(
        "TEST",
        "1D",
        data,
        evaluated_at=datetime(2027, 1, 1, tzinfo=IST),
    )

    assert result.sma50_current == pytest.approx(sum(range(11, 61)) / 50)
    assert result.sma50_seven_bars_ago == pytest.approx(sum(range(4, 54)) / 50)


def test_wilder_atr_uses_sma_seed_then_recursive_smoothing() -> None:
    data = candles([100.0] * 14 + [110.0])
    atr = CanonicalTrendEngine.wilder_atr(data)

    assert atr.iloc[13] == pytest.approx(2.0)
    assert atr.iloc[14] == pytest.approx(((2.0 * 13) + 11.0) / 14)


def test_normalized_per_candle_slope_and_angle() -> None:
    engine = CanonicalTrendEngine()
    data = candles([100.0 + index * 2.0 for index in range(60)])
    result = engine.evaluate(
        "TEST",
        "1D",
        data,
        evaluated_at=datetime(2027, 1, 1, tzinfo=IST),
    )

    expected_slope = (
        result.sma50_current - result.sma50_seven_bars_ago
    ) / (7 * result.atr14)
    assert result.normalized_slope == pytest.approx(expected_slope)
    assert result.trend_angle_degrees == pytest.approx(degrees(atan(expected_slope)))
    assert result.trend_state == CanonicalTrendState.UPTREND
    assert result.sma_colour == SmaColour.GREEN


@pytest.mark.parametrize(
    ("angle", "expected"),
    (
        (5.000001, CanonicalTrendState.UPTREND),
        (5.0, CanonicalTrendState.SIDEWAYS),
        (0.0, CanonicalTrendState.SIDEWAYS),
        (-5.0, CanonicalTrendState.SIDEWAYS),
        (-5.000001, CanonicalTrendState.DOWNTREND),
    ),
)
def test_angle_classification_boundaries(
    angle: float, expected: CanonicalTrendState
) -> None:
    assert CanonicalTrendEngine.classify_angle(angle) == expected


@pytest.mark.parametrize(
    ("closes", "state", "colour"),
    (
        (
            [100.0 + index * 2.0 for index in range(60)],
            CanonicalTrendState.UPTREND,
            SmaColour.GREEN,
        ),
        (
            [300.0 - index * 2.0 for index in range(60)],
            CanonicalTrendState.DOWNTREND,
            SmaColour.RED,
        ),
        (
            [100.0 for _ in range(60)],
            CanonicalTrendState.SIDEWAYS,
            SmaColour.NEUTRAL,
        ),
    ),
)
def test_direction_and_sma_colour(
    closes: list[float],
    state: CanonicalTrendState,
    colour: SmaColour,
) -> None:
    result = CanonicalTrendEngine().evaluate(
        "TEST",
        "1D",
        candles(closes),
        evaluated_at=datetime(2027, 1, 1, tzinfo=IST),
    )
    assert result.trend_state == state
    assert result.sma_colour == colour


def test_insufficient_history_is_unavailable_not_sideways() -> None:
    result = CanonicalTrendEngine().evaluate(
        "TEST",
        "1D",
        candles([100.0] * 56),
        evaluated_at=datetime(2027, 1, 1, tzinfo=IST),
    )
    assert result.trend_state == CanonicalTrendState.UNAVAILABLE
    assert result.reason_codes == (
        TrendReasonCode.INSUFFICIENT_CONSECUTIVE_HISTORY,
    )


def test_latest_incomplete_daily_candle_is_excluded() -> None:
    data = candles(
        [100.0 + index for index in range(58)],
        start="2026-06-16",
    )
    result = CanonicalTrendEngine().evaluate(
        "TEST",
        "1D",
        data,
        evaluated_at=datetime(2026, 8, 12, 10, 0, tzinfo=IST),
    )
    assert result.data_sufficient
    assert result.evaluation_timestamp.date().isoformat() == "2026-08-11"


def test_latest_short_segment_after_data_break_is_unavailable() -> None:
    old_segment = candles([100.0 + index for index in range(70)])
    recent_segment = candles(
        [200.0 + index for index in range(20)], start="2026-06-01"
    )
    result = CanonicalTrendEngine().evaluate_segments(
        "TEST",
        "1D",
        (old_segment, recent_segment),
        evaluated_at=datetime(2027, 1, 1, tzinfo=IST),
    )
    assert result.trend_state == CanonicalTrendState.UNAVAILABLE
    assert result.reason_codes == (
        TrendReasonCode.INSUFFICIENT_CONSECUTIVE_HISTORY,
    )


@pytest.mark.parametrize(
    ("zone_type", "state", "alignment"),
    (
        ("DEMAND", CanonicalTrendState.UPTREND, TrendAlignment.ALIGNED),
        ("DEMAND", CanonicalTrendState.DOWNTREND, TrendAlignment.OPPOSING),
        ("SUPPLY", CanonicalTrendState.DOWNTREND, TrendAlignment.ALIGNED),
        ("SUPPLY", CanonicalTrendState.UPTREND, TrendAlignment.OPPOSING),
        ("DEMAND", CanonicalTrendState.SIDEWAYS, TrendAlignment.NEUTRAL),
        ("SUPPLY", CanonicalTrendState.UNAVAILABLE, TrendAlignment.UNKNOWN),
    ),
)
def test_execution_zone_alignment_is_informational(
    zone_type: str,
    state: CanonicalTrendState,
    alignment: TrendAlignment,
) -> None:
    assert CanonicalTrendEngine.alignment(zone_type, state) == alignment
