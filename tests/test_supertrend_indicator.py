import pandas as pd
import pytest

from backend.indicators.supertrend_indicator import SuperTrendIndicator
from backend.services.indicator.indicator_service import IndicatorService


def sample_market_data():
    return pd.DataFrame(
        {
            "High": [
                110, 112, 115, 117, 119,
                121, 123, 125, 127, 130,
                132, 134, 136, 138, 140
            ],
            "Low": [
                100, 101, 103, 105, 107,
                109, 111, 113, 115, 117,
                119, 121, 123, 125, 127
            ],
            "Close": [
                105, 108, 112, 114, 116,
                118, 120, 122, 124, 128,
                130, 132, 134, 136, 138
            ]
        }
    )


def test_supertrend_returns_dataframe():
    data = sample_market_data()

    indicator = SuperTrendIndicator(
        period=10,
        multiplier=3.0
    )

    result = indicator.calculate(data)

    assert isinstance(result, pd.DataFrame)


def test_supertrend_columns_exist():
    data = sample_market_data()

    indicator = SuperTrendIndicator(
        period=10,
        multiplier=3.0
    )

    result = indicator.calculate(data)

    assert "SuperTrend" in result.columns
    assert "SuperTrend_UpperBand" in result.columns
    assert "SuperTrend_LowerBand" in result.columns
    assert "SuperTrend_Trend" in result.columns


def test_supertrend_missing_high_column_raises_error():
    data = sample_market_data().drop(
        columns=["High"]
    )

    indicator = SuperTrendIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_supertrend_service_integration():
    data = sample_market_data()

    service = IndicatorService()

    result = service.calculate_supertrend(data)

    assert isinstance(result, pd.DataFrame)
    assert "SuperTrend" in result.columns