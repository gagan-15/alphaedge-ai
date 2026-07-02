import pytest
import pandas as pd

from backend.indicators.atr_indicator import ATRIndicator


def test_atr_returns_series():
    """
    Test that ATR returns a Pandas Series.
    """

    data = pd.DataFrame({
        "High": [102, 103, 104, 105, 106,
                 107, 108, 109, 110, 111,
                 112, 113, 114, 115, 116],

        "Low": [99, 100, 101, 102, 103,
                104, 105, 106, 107, 108,
                109, 110, 111, 112, 113],

        "Close": [100, 101, 102, 103, 104,
                  105, 106, 107, 108, 109,
                  110, 111, 112, 113, 114]
    })

    indicator = ATRIndicator()

    result = indicator.calculate(data)

    assert isinstance(result, pd.Series)


def test_atr_output_length():
    """
    Test that ATR output length matches input length.
    """

    data = pd.DataFrame({
        "High": [102, 103, 104, 105, 106,
                 107, 108, 109, 110, 111,
                 112, 113, 114, 115, 116],

        "Low": [99, 100, 101, 102, 103,
                104, 105, 106, 107, 108,
                109, 110, 111, 112, 113],

        "Close": [100, 101, 102, 103, 104,
                  105, 106, 107, 108, 109,
                  110, 111, 112, 113, 114]
    })

    indicator = ATRIndicator()

    result = indicator.calculate(data)

    assert len(result) == len(data)


def test_empty_dataframe():
    """
    Test ATR with empty DataFrame.
    """

    data = pd.DataFrame()

    indicator = ATRIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_missing_high_column():
    """
    Test ATR when High column is missing.
    """

    data = pd.DataFrame({
        "Low": [100, 101],
        "Close": [101, 102]
    })

    indicator = ATRIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_missing_low_column():
    """
    Test ATR when Low column is missing.
    """

    data = pd.DataFrame({
        "High": [101, 102],
        "Close": [100, 101]
    })

    indicator = ATRIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_invalid_period():
    """
    Test ATR with invalid period.
    """

    data = pd.DataFrame({
        "High": [101, 102, 103],
        "Low": [99, 100, 101],
        "Close": [100, 101, 102]
    })

    indicator = ATRIndicator(period=0)

    with pytest.raises(ValueError):
        indicator.calculate(data)