"""
File Name:
    parabolic_sar_indicator.py

Purpose:
    Implement the Parabolic SAR indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import logging
import pandas as pd

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator


class ParabolicSARIndicator(BaseIndicator):
    """
    Parabolic SAR Indicator.
    """

    def __init__(
        self,
        acceleration: float = 0.02,
        maximum_acceleration: float = 0.20
    ):
        """
        Initialize Parabolic SAR Indicator.
        """

        self.acceleration = acceleration
        self.maximum_acceleration = maximum_acceleration
        self.logger = logging.getLogger(__name__)

    def calculate(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate Parabolic SAR.
        """

        IndicatorValidator.validate_parabolic_sar_input(data)

        self.logger.info(
            "Starting Parabolic SAR calculation with acceleration=%s, maximum_acceleration=%s",
            self.acceleration,
            self.maximum_acceleration
        )

        result = data.copy()

        high = result["High"]
        low = result["Low"]

        sar = pd.Series(
            index=result.index,
            dtype="float64"
        )

        trend = pd.Series(
            index=result.index,
            dtype="object"
        )

        if len(result) < 2:
            raise ValueError(
                "At least two rows are required to calculate Parabolic SAR."
            )

        is_uptrend = high.iloc[1] > high.iloc[0]

        acceleration_factor = self.acceleration

        if is_uptrend:
            extreme_point = high.iloc[0]
            sar.iloc[0] = low.iloc[0]
            trend.iloc[0] = "Bullish"
        else:
            extreme_point = low.iloc[0]
            sar.iloc[0] = high.iloc[0]
            trend.iloc[0] = "Bearish"

        for index in range(1, len(result)):
            previous_index = index - 1

            previous_sar = sar.iloc[previous_index]

            current_sar = previous_sar + (
                acceleration_factor * (
                    extreme_point - previous_sar
                )
            )

            if is_uptrend:
                current_sar = min(
                    current_sar,
                    low.iloc[previous_index],
                    low.iloc[index]
                )

                if low.iloc[index] < current_sar:
                    is_uptrend = False
                    current_sar = extreme_point
                    extreme_point = low.iloc[index]
                    acceleration_factor = self.acceleration
                    trend.iloc[index] = "Bearish"
                else:
                    if high.iloc[index] > extreme_point:
                        extreme_point = high.iloc[index]
                        acceleration_factor = min(
                            acceleration_factor + self.acceleration,
                            self.maximum_acceleration
                        )

                    trend.iloc[index] = "Bullish"

            else:
                current_sar = max(
                    current_sar,
                    high.iloc[previous_index],
                    high.iloc[index]
                )

                if high.iloc[index] > current_sar:
                    is_uptrend = True
                    current_sar = extreme_point
                    extreme_point = high.iloc[index]
                    acceleration_factor = self.acceleration
                    trend.iloc[index] = "Bullish"
                else:
                    if low.iloc[index] < extreme_point:
                        extreme_point = low.iloc[index]
                        acceleration_factor = min(
                            acceleration_factor + self.acceleration,
                            self.maximum_acceleration
                        )

                    trend.iloc[index] = "Bearish"

            sar.iloc[index] = current_sar

        result["ParabolicSAR"] = sar
        result["ParabolicSAR_Trend"] = trend

        self.logger.info(
            "Parabolic SAR calculation completed successfully."
        )

        return result[
            [
                "ParabolicSAR",
                "ParabolicSAR_Trend"
            ]
        ]