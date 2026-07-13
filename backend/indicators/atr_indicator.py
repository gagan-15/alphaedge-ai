"""
File Name:
    atr_indicator.py

Purpose:
    Implement the Average True Range (ATR) indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import logging
import pandas as pd

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator


class ATRIndicator(BaseIndicator):
    """
    Average True Range (ATR) Indicator.
    """

    def __init__(self, period: int = 14):
        """
        Initialize ATR Indicator.

        Args:
            period (int): ATR calculation period.
        """

        self.period = period
        self.logger = logging.getLogger(__name__)

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate Average True Range (ATR).

        Args:
            data (pd.DataFrame): Market data.

        Returns:
            pd.Series: ATR values.
        """

        IndicatorValidator.validate_common_input(data, self.period)

        IndicatorValidator.validate_minimum_rows(data, self.period)

        IndicatorValidator.validate_atr_input(data)

        self.logger.info("Starting ATR calculation with period=%s", self.period)

        # Extract required price columns
        high = data["High"]
        low = data["Low"]
        close = data["Close"]

        # Previous day's closing price
        previous_close = close.shift(1)

        # Calculate the three True Range values
        high_low = high - low

        high_previous_close = (high - previous_close).abs()

        low_previous_close = (low - previous_close).abs()

        # Calculate the True Range (TR)
        true_range = pd.concat(
            [high_low, high_previous_close, low_previous_close], axis=1
        ).max(axis=1)

        # Calculate Average True Range (ATR)
        atr = true_range.ewm(alpha=1 / self.period, adjust=False).mean()

        self.logger.info("ATR calculation completed successfully.")

        return atr
