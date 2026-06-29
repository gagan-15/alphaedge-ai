"""
File Name:
    indicator_validator.py

Purpose:
    Validate input data before calculating
    technical indicators.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd


class IndicatorValidator:
    """
    Validator for technical indicators.
    """

    @staticmethod
    def validate_common_input(data: pd.DataFrame, period: int):
        """
        Validate common input rules required by most indicators.
        """

        if data.empty:
            raise ValueError("Indicator data is empty.")

        if "Close" not in data.columns:
            raise ValueError("Required column 'Close' not found.")

        if period <= 0:
            raise ValueError("Indicator period must be greater than zero.")

    @staticmethod
    def validate_minimum_rows(data: pd.DataFrame, period: int):
        """
        Validate that enough rows are available
        for indicators that require a full period.
        """

        if len(data) < period:
            raise ValueError(
                f"Not enough data to calculate a {period}-period indicator."
            )