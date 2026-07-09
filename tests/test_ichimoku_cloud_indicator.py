import pandas as pd
import pytest

from backend.indicators.ichimoku_cloud_indicator import IchimokuCloudIndicator
from backend.services.indicator.indicator_service import IndicatorService


def sample_market_data():
    return pd.DataFrame(
        {
            "High": list(range(110, 170)),
            "Low": list(range(100, 160)),
            "Close": list(range(105, 165))
        }
    )


def test_ichimoku_returns_dataframe():
    data = sample_market_data()

    indicator = IchimokuCloudIndicator()

    result = indicator.calculate(data)

    assert isinstance(result, pd.DataFrame)


def test_ichimoku_columns_exist():
    data = sample_market_data()

    indicator = IchimokuCloudIndicator()

    result = indicator.calculate(data)

    assert "Ichimoku_ConversionLine" in result.columns
    assert "Ichimoku_BaseLine" in result.columns
    assert "Ichimoku_LeadingSpanA" in result.columns
    assert "Ichimoku_LeadingSpanB" in result.columns
    assert "Ichimoku_LaggingSpan" in result.columns


def test_ichimoku_missing_high_column_raises_error():
    data = sample_market_data().drop(
        columns=["High"]
    )

    indicator = IchimokuCloudIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_ichimoku_missing_low_column_raises_error():
    data = sample_market_data().drop(
        columns=["Low"]
    )

    indicator = IchimokuCloudIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_ichimoku_missing_close_column_raises_error():
    data = sample_market_data().drop(
        columns=["Close"]
    )

    indicator = IchimokuCloudIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_ichimoku_service_integration():
    data = sample_market_data()

    service = IndicatorService()

    result = service.calculate_ichimoku_cloud(data)

    assert isinstance(result, pd.DataFrame)
    assert "Ichimoku_ConversionLine" in result.columns