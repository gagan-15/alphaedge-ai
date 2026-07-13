"""
File Name:
    ema_indicator.py

Purpose:
    Implement the Exponential Moving Average (EMA) indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator
from backend.core.logger import logger


class EMAIndicator(BaseIndicator):
    """
    Exponential Moving Average (EMA) indicator.
    """

    def calculate(self, data, period: int = 20):
        """
        Calculate the Exponential Moving Average (EMA).

        EMA gives more weight to recent closing prices.
        """

        IndicatorValidator.validate_common_input(data, period)

        logger.info(f"Calculating {period}-period EMA.")

        data[f"EMA_{period}"] = data["Close"].ewm(span=period, adjust=False).mean()

        logger.info(f"EMA_{period} calculated successfully.")

        return data
