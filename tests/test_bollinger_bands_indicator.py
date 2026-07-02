import pytest
import pandas as pd

from backend.indicators.bollinger_bands_indicator import (
    BollingerBandsIndicator
)


def test_bollinger_returns_dataframe():
    """
    Test that Bollinger Bands returns a DataFrame.
    """

    data = pd.DataFrame({
        "Close": [
            100, 101, 102, 103, 104,
            105, 106, 107, 108, 109,
            110, 111, 112, 113, 114,
            115, 116, 117, 118, 119
        ]
    })

    indicator = BollingerBandsIndicator()

    result = indicator.calculate(data)

    assert isinstance(result, pd.DataFrame)


def test_bollinger_has_required_columns():
    """
    Test that all Bollinger Band columns exist.
    """

    data = pd.DataFrame({
        "Close": [
            100, 101, 102, 103, 104,
            105, 106, 107, 108, 109,
            110, 111, 112, 113, 114,
            115, 116, 117, 118, 119
        ]
    })

    indicator = BollingerBandsIndicator()

    result = indicator.calculate(data)

    assert "Middle Band" in result.columns
    assert "Upper Band" in result.columns
    assert "Lower Band" in result.columns


def test_bollinger_output_length():
    """
    Test that output length matches input length.
    """

    data = pd.DataFrame({
        "Close": [
            100, 101, 102, 103, 104,
            105, 106, 107, 108, 109,
            110, 111, 112, 113, 114,
            115, 116, 117, 118, 119
        ]
    })

    indicator = BollingerBandsIndicator()

    result = indicator.calculate(data)

    assert len(result) == len(data)


def test_empty_dataframe():
    """
    Test empty DataFrame.
    """

    data = pd.DataFrame()

    indicator = BollingerBandsIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_missing_close_column():
    """
    Test missing Close column.
    """

    data = pd.DataFrame({
        "Open": [100, 101, 102]
    })

    indicator = BollingerBandsIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_invalid_period():
    """
    Test invalid period.
    """

    data = pd.DataFrame({
        "Close": [
            100, 101, 102, 103, 104
        ]
    })

    indicator = BollingerBandsIndicator(
        period=0
    )

    with pytest.raises(ValueError):
        indicator.calculate(data)