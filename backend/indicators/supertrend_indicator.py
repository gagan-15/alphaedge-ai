"""
File Name:
    supertrend_indicator.py

Purpose:
    Implement the SuperTrend indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import logging
import pandas as pd

from backend.indicators.base_indicator import BaseIndicator
from backend.indicators.atr_indicator import ATRIndicator
from backend.validators.indicator_validator import IndicatorValidator


class SuperTrendIndicator(BaseIndicator):
    """
    SuperTrend Indicator.
    """

    def __init__(
        self,
        period: int = 10,
        multiplier: float = 3.0
    ):
        """
        Initialize SuperTrend Indicator.
        """

        self.period = period
        self.multiplier = multiplier
        self.logger = logging.getLogger(__name__)

    def calculate(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate SuperTrend.
        """

        IndicatorValidator.validate_common_input(
            data,
            self.period
        )

        IndicatorValidator.validate_minimum_rows(
            data,
            self.period
        )

        IndicatorValidator.validate_supertrend_input(data)

        self.logger.info(
            "Starting SuperTrend calculation with period=%s, multiplier=%s",
            self.period,
            self.multiplier
        )

        result = data.copy()

        atr_indicator = ATRIndicator(self.period)
        atr = atr_indicator.calculate(result)

        hl2 = (
            result["High"] + result["Low"]
        ) / 2

        basic_upper_band = hl2 + (
            self.multiplier * atr
        )

        basic_lower_band = hl2 - (
            self.multiplier * atr
        )

        final_upper_band = basic_upper_band.copy()
        final_lower_band = basic_lower_band.copy()

        supertrend = pd.Series(
            index=result.index,
            dtype="float64"
        )

        trend = pd.Series(
            index=result.index,
            dtype="object"
        )

        for index in range(1, len(result)):
            previous_index = index - 1

            if (
                basic_upper_band.iloc[index]
                < final_upper_band.iloc[previous_index]
                or result["Close"].iloc[previous_index]
                > final_upper_band.iloc[previous_index]
            ):
                final_upper_band.iloc[index] = basic_upper_band.iloc[index]
            else:
                final_upper_band.iloc[index] = final_upper_band.iloc[
                    previous_index
                ]

            if (
                basic_lower_band.iloc[index]
                > final_lower_band.iloc[previous_index]
                or result["Close"].iloc[previous_index]
                < final_lower_band.iloc[previous_index]
            ):
                final_lower_band.iloc[index] = basic_lower_band.iloc[index]
            else:
                final_lower_band.iloc[index] = final_lower_band.iloc[
                    previous_index
                ]

            if index == 1:
                supertrend.iloc[index] = final_upper_band.iloc[index]

            elif (
                supertrend.iloc[previous_index]
                == final_upper_band.iloc[previous_index]
            ):
                if result["Close"].iloc[index] <= final_upper_band.iloc[index]:
                    supertrend.iloc[index] = final_upper_band.iloc[index]
                else:
                    supertrend.iloc[index] = final_lower_band.iloc[index]

            else:
                if result["Close"].iloc[index] >= final_lower_band.iloc[index]:
                    supertrend.iloc[index] = final_lower_band.iloc[index]
                else:
                    supertrend.iloc[index] = final_upper_band.iloc[index]

            if result["Close"].iloc[index] >= supertrend.iloc[index]:
                trend.iloc[index] = "Bullish"
            else:
                trend.iloc[index] = "Bearish"

        result["SuperTrend"] = supertrend
        result["SuperTrend_UpperBand"] = final_upper_band
        result["SuperTrend_LowerBand"] = final_lower_band
        result["SuperTrend_Trend"] = trend

        self.logger.info(
            "SuperTrend calculation completed successfully."
        )

        return result[
            [
                "SuperTrend",
                "SuperTrend_UpperBand",
                "SuperTrend_LowerBand",
                "SuperTrend_Trend"
            ]
        ]