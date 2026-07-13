"""
File Name:
    volume_sma_indicator.py

Purpose:
    Implement the Volume Simple Moving Average (Volume SMA) indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator
from backend.core.logger import logger


class VolumeSMAIndicator(BaseIndicator):
    """
    Volume Simple Moving Average (Volume SMA) indicator.
    """

    def calculate(self, data, period: int = 20):
        """
        Calculate the Volume Simple Moving Average.

        Args:
            data (pd.DataFrame):
                Market data containing the Volume column.

            period (int):
                Number of candles used to calculate
                the moving average.

        Returns:
            pd.DataFrame:
                Input DataFrame with a new
                Volume_SMA_<period> column.
        """

        if data.empty:
            raise ValueError("Indicator data is empty.")

        if "Volume" not in data.columns:
            raise ValueError("Required column 'Volume' not found.")

        IndicatorValidator.validate_period(period)
        IndicatorValidator.validate_minimum_rows(data, period)

        data[f"Volume_SMA_{period}"] = data["Volume"].rolling(window=period).mean()

        logger.info(f"Calculated {period}-period Volume SMA successfully.")

        return data
