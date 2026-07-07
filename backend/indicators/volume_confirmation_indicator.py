"""
File Name:
    volume_confirmation_indicator.py

Purpose:
    Implement the Volume Confirmation indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.base_indicator import BaseIndicator
from backend.indicators.relative_volume_indicator import (
    RelativeVolumeIndicator
)
from backend.validators.indicator_validator import IndicatorValidator
from backend.core.logger import logger


class VolumeConfirmationIndicator(BaseIndicator):
    """
    Volume Confirmation indicator.
    """

    def calculate(
        self,
        data,
        period: int = 20
    ):
        """
        Calculate Volume Confirmation.

        Args:
            data:
                Market data.

            period:
                Relative Volume period.

        Returns:
            pd.DataFrame
        """

        if data.empty:
            raise ValueError("Indicator data is empty.")

        if "Volume" not in data.columns:
            raise ValueError(
                "Required column 'Volume' not found."
            )

        IndicatorValidator.validate_period(period)
        IndicatorValidator.validate_minimum_rows(
            data,
            period
        )

        relative_volume_indicator = RelativeVolumeIndicator()

        data = relative_volume_indicator.calculate(
            data,
            period
        )

        def classify_volume(rvol):
            """
            Classify Relative Volume.
            """

            if pd.isna(rvol):
                return None

            if rvol < 0.5:
                return "Very Low"

            if rvol < 1.0:
                return "Low"

            if rvol < 1.5:
                return "Normal"

            if rvol < 2.0:
                return "High"

            return "Very High"

        data["Volume_Confirmation"] = (
            data[f"RVOL_{period}"]
            .apply(classify_volume)
        )

        logger.info(
            "Calculated Volume Confirmation successfully."
        )

        return data