"""Canonical OHLC validation tests for Milestone 1.1."""

import numpy as np
import pandas as pd
import pytest

from backend.validators.market_data_validator import (
    MarketDataValidationError,
    MarketDataValidator,
)


def valid_market_data() -> pd.DataFrame:
    """Return valid OHLCV data that validation must not mutate."""

    return pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1000, 1200],
        },
        index=pd.date_range("2026-01-01", periods=2, freq="D"),
    )


def assert_validation_error(
    data: pd.DataFrame,
    reason_code: str,
) -> None:
    with pytest.raises(MarketDataValidationError) as raised:
        MarketDataValidator.validate(data)

    assert raised.value.reason_code == reason_code


def test_valid_data_is_accepted_without_mutation() -> None:
    data = valid_market_data()
    original = data.copy(deep=True)

    MarketDataValidator.validate(data)

    pd.testing.assert_frame_equal(data, original)


@pytest.mark.parametrize("column", ["Open", "High", "Low", "Close"])
def test_missing_ohlc_column_is_rejected(column: str) -> None:
    assert_validation_error(
        valid_market_data().drop(columns=column),
        "MARKET_DATA_MISSING_REQUIRED_COLUMN",
    )


def test_missing_ohlc_value_is_rejected() -> None:
    data = valid_market_data()
    data.loc[data.index[0], "Close"] = np.nan

    assert_validation_error(data, "MARKET_DATA_MISSING_VALUE")


def test_non_numeric_ohlc_is_rejected() -> None:
    data = valid_market_data()
    data["Open"] = data["Open"].astype(object)
    data.loc[data.index[0], "Open"] = "invalid"

    assert_validation_error(data, "MARKET_DATA_OHLC_NON_NUMERIC")


@pytest.mark.parametrize("value", [np.inf, -np.inf])
def test_non_finite_ohlc_is_rejected(value: float) -> None:
    data = valid_market_data()
    data.loc[data.index[0], "High"] = value

    assert_validation_error(data, "MARKET_DATA_OHLC_NON_FINITE")


@pytest.mark.parametrize("value", [0.0, -1.0])
def test_non_positive_ohlc_is_rejected(value: float) -> None:
    data = valid_market_data()
    data.loc[data.index[0], "Low"] = value

    assert_validation_error(data, "MARKET_DATA_OHLC_NON_POSITIVE")


def test_high_below_low_is_rejected() -> None:
    data = valid_market_data()
    data.loc[data.index[0], ["High", "Low"]] = [98.0, 99.0]

    assert_validation_error(data, "MARKET_DATA_HIGH_BELOW_LOW")


def test_zero_range_candle_is_rejected() -> None:
    data = valid_market_data()
    data.loc[data.index[0], ["Open", "High", "Low", "Close"]] = [
        100.0,
        100.0,
        100.0,
        100.0,
    ]

    assert_validation_error(data, "MARKET_DATA_ZERO_RANGE")


def test_open_outside_range_is_rejected() -> None:
    data = valid_market_data()
    data.loc[data.index[0], "Open"] = 103.0

    assert_validation_error(data, "MARKET_DATA_OPEN_OUTSIDE_RANGE")


def test_close_outside_range_is_rejected() -> None:
    data = valid_market_data()
    data.loc[data.index[0], "Close"] = 98.0

    assert_validation_error(data, "MARKET_DATA_CLOSE_OUTSIDE_RANGE")


def test_validation_error_remains_a_value_error() -> None:
    data = valid_market_data()
    data.loc[data.index[0], "Close"] = np.nan

    with pytest.raises(ValueError, match="missing values"):
        MarketDataValidator.validate(data)
