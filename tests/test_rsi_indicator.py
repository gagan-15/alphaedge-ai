import pytest
import pandas as pd

from backend.indicators.rsi_indicator import RSIIndicator


def test_rsi_returns_series():
    data = pd.DataFrame(
        {
            "Close": [
                100,
                102,
                101,
                103,
                105,
                104,
                106,
                108,
                107,
                110,
                112,
                111,
                113,
                115,
                116,
            ]
        }
    )

    indicator = RSIIndicator()

    result = indicator.calculate(data)

    assert isinstance(result, pd.Series)


def test_rsi_output_length():
    data = pd.DataFrame(
        {
            "Close": [
                100,
                102,
                101,
                103,
                105,
                104,
                106,
                108,
                107,
                110,
                112,
                111,
                113,
                115,
                116,
            ]
        }
    )

    indicator = RSIIndicator()

    result = indicator.calculate(data)

    assert len(result) == len(data)


def test_rsi_values_between_0_and_100():
    data = pd.DataFrame(
        {
            "Close": [
                100,
                102,
                101,
                103,
                105,
                104,
                106,
                108,
                107,
                110,
                112,
                111,
                113,
                115,
                116,
            ]
        }
    )

    indicator = RSIIndicator()

    result = indicator.calculate(data)

    assert result.min() >= 0
    assert result.max() <= 100


def test_empty_dataframe():
    data = pd.DataFrame()

    indicator = RSIIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_missing_close_column():
    data = pd.DataFrame({"Open": [100, 101, 102]})

    indicator = RSIIndicator()

    with pytest.raises(ValueError):
        indicator.calculate(data)


def test_invalid_period():
    data = pd.DataFrame({"Close": [100, 101, 102, 103, 104]})

    indicator = RSIIndicator(period=0)

    with pytest.raises(ValueError):
        indicator.calculate(data)
