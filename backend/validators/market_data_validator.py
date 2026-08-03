"""
File Name:
    market_data_validator.py

Purpose:
    Validate downloaded market data before it is
    used by the application.

Description:
    Ensures market data is complete, consistent,
    and ready for further processing.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

from typing import Final

import numpy as np
import pandas as pd


class MarketDataValidationError(ValueError):
    """Market-data validation failure with a stable reason code."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        *,
        row_label: object | None = None,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.row_label = row_label


class MarketDataValidator:
    """
    Responsible for validating market data.
    """

    @staticmethod
    def validate_not_empty(data: pd.DataFrame):
        """
        Validate that market data is not empty.
        """

        if data.empty:
            raise MarketDataValidationError(
                "MARKET_DATA_EMPTY",
                "Market data is empty.",
            )

    @staticmethod
    def validate_required_columns(data: pd.DataFrame):
        """
        Validate that all required market data columns exist.
        """

        for column in MarketDataValidator.REQUIRED_COLUMNS:
            if column not in data.columns:
                raise MarketDataValidationError(
                    "MARKET_DATA_MISSING_REQUIRED_COLUMN",
                    f"Required column '{column}' is missing.",
                )

    @staticmethod
    def validate_missing_values(data: pd.DataFrame):
        """
        Validate that market data does not contain
        any missing (NaN) values.
        """

        if data.isnull().values.any():
            raise MarketDataValidationError(
                "MARKET_DATA_MISSING_VALUE",
                "Market data contains missing values.",
            )

    @classmethod
    def validate_ohlc_integrity(cls, data: pd.DataFrame) -> None:
        """Validate canonical OHLC structure without repairing source data."""

        ohlc = data.loc[:, cls.OHLC_COLUMNS]
        numeric_ohlc = ohlc.apply(pd.to_numeric, errors="coerce")

        invalid_numeric = numeric_ohlc.isna() & ~ohlc.isna()
        if invalid_numeric.any(axis=None):
            row_label = invalid_numeric.any(axis=1).idxmax()
            raise MarketDataValidationError(
                "MARKET_DATA_OHLC_NON_NUMERIC",
                f"Market data contains non-numeric OHLC values at row {row_label!r}.",
                row_label=row_label,
            )

        finite_rows = np.isfinite(numeric_ohlc.to_numpy(dtype=float)).all(axis=1)
        if not finite_rows.all():
            row_label = data.index[int(np.flatnonzero(~finite_rows)[0])]
            raise MarketDataValidationError(
                "MARKET_DATA_OHLC_NON_FINITE",
                f"Market data contains non-finite OHLC values at row {row_label!r}.",
                row_label=row_label,
            )

        positive_rows = (numeric_ohlc > 0).all(axis=1)
        if not positive_rows.all():
            row_label = positive_rows.index[~positive_rows][0]
            raise MarketDataValidationError(
                "MARKET_DATA_OHLC_NON_POSITIVE",
                f"Market data contains non-positive OHLC values at row {row_label!r}.",
                row_label=row_label,
            )

        high_below_low = numeric_ohlc["High"] < numeric_ohlc["Low"]
        if high_below_low.any():
            row_label = high_below_low.index[high_below_low][0]
            raise MarketDataValidationError(
                "MARKET_DATA_HIGH_BELOW_LOW",
                f"Market data High is below Low at row {row_label!r}.",
                row_label=row_label,
            )

        zero_range = numeric_ohlc["High"] == numeric_ohlc["Low"]
        if zero_range.any():
            row_label = zero_range.index[zero_range][0]
            raise MarketDataValidationError(
                "MARKET_DATA_ZERO_RANGE",
                f"Market data contains a zero-range candle at row {row_label!r}.",
                row_label=row_label,
            )

        open_outside = (numeric_ohlc["Open"] > numeric_ohlc["High"]) | (
            numeric_ohlc["Open"] < numeric_ohlc["Low"]
        )
        if open_outside.any():
            row_label = open_outside.index[open_outside][0]
            raise MarketDataValidationError(
                "MARKET_DATA_OPEN_OUTSIDE_RANGE",
                f"Market data Open is outside High-Low range at row {row_label!r}.",
                row_label=row_label,
            )

        close_outside = (numeric_ohlc["Close"] > numeric_ohlc["High"]) | (
            numeric_ohlc["Close"] < numeric_ohlc["Low"]
        )
        if close_outside.any():
            row_label = close_outside.index[close_outside][0]
            raise MarketDataValidationError(
                "MARKET_DATA_CLOSE_OUTSIDE_RANGE",
                f"Market data Close is outside High-Low range at row {row_label!r}.",
                row_label=row_label,
            )

    @staticmethod
    def validate_duplicate_dates(data: pd.DataFrame):
        """
        Validate that market data does not contain
        duplicate dates.
        """

        if data.index.duplicated().any():
            raise MarketDataValidationError(
                "MARKET_DATA_DUPLICATE_DATES",
                "Market data contains duplicate dates.",
            )

    @staticmethod
    def validate_sorted_dates(data: pd.DataFrame):
        """
        Validate that market data is sorted by date
        in ascending order.
        """

        if not data.index.is_monotonic_increasing:
            raise MarketDataValidationError(
                "MARKET_DATA_UNSORTED_DATES",
                "Market data is not sorted by date.",
            )

    @staticmethod
    def validate(data: pd.DataFrame):
        """
        Run all market data validation rules.
        """

        MarketDataValidator.validate_not_empty(data)
        MarketDataValidator.validate_required_columns(data)
        MarketDataValidator.validate_missing_values(data)
        MarketDataValidator.validate_ohlc_integrity(data)
        MarketDataValidator.validate_duplicate_dates(data)
        MarketDataValidator.validate_sorted_dates(data)
    OHLC_COLUMNS: Final[tuple[str, ...]] = (
        "Open",
        "High",
        "Low",
        "Close",
    )

    REQUIRED_COLUMNS: Final[tuple[str, ...]] = (*OHLC_COLUMNS, "Volume")
