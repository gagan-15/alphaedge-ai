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
        
    @staticmethod
    def validate_period(period: int) -> None:
        """
        Validate indicator period.

        Args:
            period (int): Indicator period.

        Raises:
            ValueError: If period is not a positive integer.
        """
        if not isinstance(period, int):
            raise ValueError("Indicator period must be an integer.")

        if period <= 0:
            raise ValueError("Indicator period must be greater than zero.")
        

    @staticmethod
    def validate_atr_input(data: pd.DataFrame) -> None:
        """
        Validate input data required for ATR calculation.

        Args:
            data (pd.DataFrame): Market data.

        Raises:
            ValueError: If required columns are missing.
        """

        required_columns = [
            "High",
            "Low",
            "Close"
        ]

        for column in required_columns:
            if column not in data.columns:
                raise ValueError(
                    f"Required column '{column}' not found."
                )
            
    @staticmethod
    def validate_vwap_input(data: pd.DataFrame) -> None:
        """
        Validate input data required for VWAP calculation.

        Args:
            data (pd.DataFrame): Market data.

        Raises:
            ValueError: If required columns are missing.
        """

        required_columns = [
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        for column in required_columns:
            if column not in data.columns:
                raise ValueError(
                    f"Required column '{column}' not found."
                )
            
    @staticmethod
    def validate_obv_input(data: pd.DataFrame) -> None:
        """
        Validate input data required for OBV calculation.
        """

        required_columns = [
            "Close",
            "Volume"
        ]

        for column in required_columns:
            if column not in data.columns:
                raise ValueError(
                    f"Required column '{column}' not found."
                )
            

    @staticmethod
    def validate_obv_input(data: pd.DataFrame) -> None:
        """
        Validate input data required for OBV calculation.
        """

        required_columns = [
            "Close",
            "Volume"
        ]

        for column in required_columns:
            if column not in data.columns:
                raise ValueError(
                    f"Required column '{column}' not found."
                )