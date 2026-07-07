"""
File Name:
    vwap_indicator.py

Purpose:
    Implement the Volume Weighted Average Price (VWAP) indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator
from backend.core.logger import logger


class VWAPIndicator(BaseIndicator):
    """
    Volume Weighted Average Price (VWAP) indicator.
    """

    def calculate(self, data):
        """
        Calculate Session VWAP.

        Args:
            data:
                Market data.

        Returns:
            pd.DataFrame
        """

        if data.empty:
            raise ValueError("Indicator data is empty.")

        IndicatorValidator.validate_vwap_input(data)

        typical_price = (
            data["High"] +
            data["Low"] +
            data["Close"]
        ) / 3

        tp_volume = (
            typical_price *
            data["Volume"]
        )

        cumulative_tp_volume = tp_volume.cumsum()

        cumulative_volume = (
            data["Volume"]
            .cumsum()
        )

        data["VWAP"] = (
            cumulative_tp_volume /
            cumulative_volume
        )

        logger.info(
            "Calculated Session VWAP successfully."
        )

        return data