"""
File Name:
    bollinger_bands_indicator.py

Purpose:
    Implement the Bollinger Bands indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import logging
import pandas as pd

from backend.indicators.base_indicator import BaseIndicator
from backend.indicators.sma_indicator import SMAIndicator
from backend.validators.indicator_validator import IndicatorValidator


class BollingerBandsIndicator(BaseIndicator):
    """
    Bollinger Bands indicator.
    """

    def __init__(
        self,
        period: int = 20,
        multiplier: int = 2
    ):
        """
        Initialize Bollinger Bands.
        """

        self.period = period
        self.multiplier = multiplier
        self.logger = logging.getLogger(__name__)


    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.

        Args:
            data (pd.DataFrame): Market data containing the Close column.

        Returns:
            pd.DataFrame: Middle Band, Upper Band and Lower Band.
        """

        IndicatorValidator.validate_common_input(
            data,
            self.period
        )

        IndicatorValidator.validate_minimum_rows(
            data,
            self.period
        )

        self.logger.info(
            "Starting Bollinger Bands calculation "
            "with period=%s and multiplier=%s",
            self.period,
            self.multiplier
        )

            # Calculate the Middle Band using SMA
        sma_indicator = SMAIndicator()

        result = sma_indicator.calculate(
            data.copy(),
            self.period
        )

        middle_band = result[
            f"SMA_{self.period}"
        ]

            # Calculate Standard Deviation
        standard_deviation = data[
            "Close"
        ].rolling(
            window=self.period
        ).std()

                # Calculate Upper and Lower Bands
        upper_band = middle_band + (
            standard_deviation * self.multiplier
        )

        lower_band = middle_band - (
            standard_deviation * self.multiplier
        )

                # Prepare the result
        result = pd.DataFrame({
            "Middle Band": middle_band,
            "Upper Band": upper_band,
            "Lower Band": lower_band
        })

        self.logger.info(
            "Bollinger Bands calculation completed successfully."
        )

        return result