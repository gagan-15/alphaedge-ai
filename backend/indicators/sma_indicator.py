"""
File Name:
    sma_indicator.py

Purpose:
    Implement the Simple Moving Average (SMA) indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator
from backend.core.logger import logger

class SMAIndicator(BaseIndicator):
    """
    Simple Moving Average (SMA) indicator.
    """

    def calculate(self, data, period: int = 20):
        """
        Calculate the Simple Moving Average (SMA).

        SMA is calculated using the average closing price
        over a specified number of candles.
        """
        IndicatorValidator.validate_common_input(data, period)
        IndicatorValidator.validate_minimum_rows(data, period)

        data[f"SMA_{period}"] = data["Close"].rolling(
            window=period
        ).mean()

        logger.info(
             f"Calculating {period}-period SMA."
         )

        return data