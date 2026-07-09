"""
File Name:
    ichimoku_cloud_indicator.py

Purpose:
    Implement the Ichimoku Cloud indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import logging
import pandas as pd

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator


class IchimokuCloudIndicator(BaseIndicator):
    """
    Ichimoku Cloud Indicator.
    """

    def __init__(
        self,
        conversion_period: int = 9,
        base_period: int = 26,
        leading_span_b_period: int = 52,
        displacement: int = 26
    ):
        """
        Initialize Ichimoku Cloud Indicator.
        """

        self.conversion_period = conversion_period
        self.base_period = base_period
        self.leading_span_b_period = leading_span_b_period
        self.displacement = displacement
        self.logger = logging.getLogger(__name__)

    def calculate(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate Ichimoku Cloud.
        """

        IndicatorValidator.validate_ichimoku_input(data)

        self.logger.info(
            "Starting Ichimoku Cloud calculation."
        )

        result = data.copy()

        high = result["High"]
        low = result["Low"]
        close = result["Close"]

        conversion_line = (
            high.rolling(
                window=self.conversion_period
            ).max()
            +
            low.rolling(
                window=self.conversion_period
            ).min()
        ) / 2

        base_line = (
            high.rolling(
                window=self.base_period
            ).max()
            +
            low.rolling(
                window=self.base_period
            ).min()
        ) / 2

        leading_span_a = (
            (
                conversion_line + base_line
            ) / 2
        ).shift(self.displacement)

        leading_span_b = (
            (
                high.rolling(
                    window=self.leading_span_b_period
                ).max()
                +
                low.rolling(
                    window=self.leading_span_b_period
                ).min()
            ) / 2
        ).shift(self.displacement)

        lagging_span = close.shift(
            -self.displacement
        )

        result["Ichimoku_ConversionLine"] = conversion_line
        result["Ichimoku_BaseLine"] = base_line
        result["Ichimoku_LeadingSpanA"] = leading_span_a
        result["Ichimoku_LeadingSpanB"] = leading_span_b
        result["Ichimoku_LaggingSpan"] = lagging_span

        self.logger.info(
            "Ichimoku Cloud calculation completed successfully."
        )

        return result[
            [
                "Ichimoku_ConversionLine",
                "Ichimoku_BaseLine",
                "Ichimoku_LeadingSpanA",
                "Ichimoku_LeadingSpanB",
                "Ichimoku_LaggingSpan"
            ]
        ]