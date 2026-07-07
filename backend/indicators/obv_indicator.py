"""
File Name:
    obv_indicator.py

Purpose:
    Implement the On-Balance Volume (OBV) indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator
from backend.core.logger import logger


class OBVIndicator(BaseIndicator):
    """
    On-Balance Volume (OBV) indicator.
    """

    def calculate(self, data):
        """
        Calculate On-Balance Volume (OBV).

        Args:
            data:
                Market data.

        Returns:
            pd.DataFrame
        """

        if data.empty:
            raise ValueError("Indicator data is empty.")

        IndicatorValidator.validate_obv_input(data)

        obv_values = [0]

        for index in range(1, len(data)):
            previous_obv = obv_values[-1]

            current_close = data["Close"].iloc[index]
            previous_close = data["Close"].iloc[index - 1]
            current_volume = data["Volume"].iloc[index]

            if current_close > previous_close:
                obv_values.append(
                    previous_obv + current_volume
                )

            elif current_close < previous_close:
                obv_values.append(
                    previous_obv - current_volume
                )

            else:
                obv_values.append(previous_obv)

        data["OBV"] = obv_values

        logger.info(
            "Calculated OBV successfully."
        )

        return data