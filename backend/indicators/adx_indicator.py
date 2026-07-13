"""
File Name:
    adx_indicator.py

Purpose:
    Calculate the Average Directional Index (ADX),
    Positive Directional Indicator (+DI),
    and Negative Directional Indicator (-DI).

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import logging

import pandas as pd

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator

logger = logging.getLogger(__name__)


class ADXIndicator(BaseIndicator):
    """
    Average Directional Index (ADX) Indicator.
    """

    def calculate(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate ADX, +DI and -DI.

        Args:
            data:
                Market data.

            period:
                ADX calculation period.

        Returns:
            pd.DataFrame:
                DataFrame containing ADX,
                +DI and -DI columns.
        """

        logger.info("Starting ADX calculation.")

        IndicatorValidator.validate_period(period)
        IndicatorValidator.validate_adx_input(data)
        IndicatorValidator.validate_minimum_rows(data, period)

        result = data.copy()

        high_diff = result["High"].diff()

        low_diff = -result["Low"].diff()

        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)

        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        high_low = result["High"] - result["Low"]

        high_close = (result["High"] - result["Close"].shift()).abs()

        low_close = (result["Low"] - result["Close"].shift()).abs()

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        atr = true_range.rolling(window=period).mean()

        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)

        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        dx = (((plus_di - minus_di).abs()) / (plus_di + minus_di)) * 100

        result["+DI"] = plus_di

        result["-DI"] = minus_di

        result["ADX"] = dx.rolling(window=period).mean()

        logger.info("ADX calculation completed successfully.")

        return result
