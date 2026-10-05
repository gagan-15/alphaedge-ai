"""Milestone 1.2 canonical candle-classification tests."""

import pandas as pd
import pytest

from backend.engines.demand_supply_engine.candle_classifier import CandleClassifier
from backend.models.candle_classification import CandleDirection, CandleStructure


def _frame(rows: list[tuple[float, float, float, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"])


@pytest.mark.parametrize(
    ("row", "direction", "structure"),
    [
        ((10, 12, 8, 11), CandleDirection.BULLISH, CandleStructure.BASE),
        ((11, 12, 8, 9), CandleDirection.BEARISH, CandleStructure.BOUNDARY),
        ((9, 12, 8, 12), CandleDirection.BULLISH, CandleStructure.EXCITING),
        ((11, 12, 8, 8), CandleDirection.BEARISH, CandleStructure.EXCITING),
        ((10, 12, 8, 10), CandleDirection.NEUTRAL, CandleStructure.BASE),
    ],
)
def test_canonical_direction_and_body_ratio_classification(
    row: tuple[float, float, float, float],
    direction: CandleDirection,
    structure: CandleStructure,
) -> None:
    result = CandleClassifier().classify(_frame([row]), 0)

    assert result.direction == direction
    assert result.structure == structure


def test_exactly_fifty_percent_is_neither_base_nor_exciting() -> None:
    result = CandleClassifier().classify(_frame([(10, 14, 8, 13)]), 0)

    assert result.body_ratio == 0.5
    assert result.structure == CandleStructure.BOUNDARY


def test_explosive_requires_body_range_and_directional_close() -> None:
    normal = [(10, 11, 9, 10.6)] * 20
    data = _frame([*normal, (10, 14, 10, 13.8)])

    result = CandleClassifier().classify(data, 20)

    assert result.explosive is True
    assert result.range_to_median == 2.0
    assert result.close_location == pytest.approx(0.05)


def test_explosive_is_false_without_full_twenty_candle_history() -> None:
    result = CandleClassifier().classify(
        _frame([(10, 11, 9, 10.6), (10, 14, 10, 13.8)]), 1
    )

    assert result.explosive is False
    assert result.range_to_median is None


def test_zero_range_is_rejected_at_classification_boundary() -> None:
    with pytest.raises(ValueError, match="positive range"):
        CandleClassifier().classify(_frame([(10, 10, 10, 10)]), 0)
