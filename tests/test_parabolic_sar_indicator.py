import pandas as pd
import pytest

from backend.indicators.parabolic_sar_indicator import ParabolicSARIndicator
from backend.services.indicator.indicator_service import IndicatorService


def sample_market_data():
    return pd.DataFrame(
        {
            "High": [
                110, 112, 115, 117, 119,
                121, 123, 125, 127, 130
            ],
            "Low": [
                100, 101, 103, 105, 107,
                109, 111, 113, 115, 117
            ]
        }
    )


def test_parabolic_sar_returns_dataframe():
    data = sample_market_data()

    indicator = ParabolicSARIndicator()

    result = indicator.calculate(data)

    assert isinstance(result, pd.DataFrame)


def test_parabolic_sar_columns_exist():
    data = sample_market_data()

    indicator = ParabolicSARIndicator()

    result = indicator.calculate(data)

    assert "ParabolicSAR" in result.columns
    assert "ParabolicSAR_Trend" in result.columns


def test_parabolic_sar_missing_high_column_raises_error():
    data = sample_market_data().drop(
        columns=["High"]
    )

    indicator = ParabolicSARIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_parabolic_sar_missing_low_column_raises_error():
    data = sample_market_data().drop(
        columns=["Low"]
    )

    indicator = ParabolicSARIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_parabolic_sar_service_integration():
    data = sample_market_data()

    service = IndicatorService()

    result = service.calculate_parabolic_sar(data)

    assert isinstance(result, pd.DataFrame)
    assert "ParabolicSAR" in result.columns