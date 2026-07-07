"""
File Name:
    relative_volume_indicator.py

Purpose:
    Implement the Relative Volume (RVOL) indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

from backend.indicators.base_indicator import BaseIndicator
from backend.indicators.volume_sma_indicator import VolumeSMAIndicator
from backend.validators.indicator_validator import IndicatorValidator
from backend.core.logger import logger


class RelativeVolumeIndicator(BaseIndicator):
    """
    Relative Volume (RVOL) indicator.
    """

    def calculate(self, data, period: int = 20):
        """
        Calculate Relative Volume (RVOL).

        RVOL compares current volume against
        average volume over a selected period.
        """

        if data.empty:
            raise ValueError("Indicator data is empty.")

        if "Volume" not in data.columns:
            raise ValueError("Required column 'Volume' not found.")

        IndicatorValidator.validate_period(period)
        IndicatorValidator.validate_minimum_rows(data, period)

        volume_sma_indicator = VolumeSMAIndicator()

        data = volume_sma_indicator.calculate(
            data,
            period
        )

        data[f"RVOL_{period}"] = (
            data["Volume"] / data[f"Volume_SMA_{period}"]
        )

        logger.info(
            f"Calculated {period}-period RVOL successfully."
        )

        return data