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

import pandas as pd


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
            raise ValueError("Market data is empty.")
        

    @staticmethod
    def validate_required_columns(data: pd.DataFrame):
        """
        Validate that all required market data columns exist.
        """

        required_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        for column in required_columns:
            if column not in data.columns:
                raise ValueError(
                    f"Required column '{column}' is missing."
                )  
            
    @staticmethod
    def validate_missing_values(data: pd.DataFrame):
        """
        Validate that market data does not contain
        any missing (NaN) values.
        """

        if data.isnull().values.any():
            raise ValueError(
                "Market data contains missing values."
            )
        
    @staticmethod
    def validate_duplicate_dates(data: pd.DataFrame):
        """
        Validate that market data does not contain
        duplicate dates.
        """

        if data.index.duplicated().any():
            raise ValueError(
                "Market data contains duplicate dates."
            )
        
    @staticmethod
    def validate_sorted_dates(data: pd.DataFrame):
        """
        Validate that market data is sorted by date
        in ascending order.
        """

        if not data.index.is_monotonic_increasing:
            raise ValueError(
                "Market data is not sorted by date."
            )
        
    @staticmethod
    def validate(data: pd.DataFrame):
        """
        Run all market data validation rules.
        """

        MarketDataValidator.validate_not_empty(data)
        MarketDataValidator.validate_required_columns(data)
        MarketDataValidator.validate_missing_values(data)
        MarketDataValidator.validate_duplicate_dates(data)
        MarketDataValidator.validate_sorted_dates(data)