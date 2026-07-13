"""
File Name:
    mfi_indicator.py

Purpose:
    Calculate the Money Flow Index (MFI) indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import logging

import pandas as pd

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator

logger = logging.getLogger(__name__)


class MFIIndicator(BaseIndicator):
    """
    Money Flow Index (MFI) Indicator.
    """

    def calculate(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate the Money Flow Index (MFI).

        Args:
            data:
                Market data.

            period:
                MFI calculation period.

        Returns:
            pd.DataFrame:
                DataFrame containing the MFI column.
        """

        logger.info("Starting MFI calculation.")

        IndicatorValidator.validate_period(period)
        IndicatorValidator.validate_mfi_input(data)
        IndicatorValidator.validate_minimum_rows(data, period)

        result = data.copy()

        typical_price = (result["High"] + result["Low"] + result["Close"]) / 3

        raw_money_flow = typical_price * result["Volume"]

        typical_price_change = typical_price.diff()

        positive_money_flow = raw_money_flow.where(typical_price_change > 0, 0)

        negative_money_flow = raw_money_flow.where(typical_price_change < 0, 0)

        rolling_positive_money_flow = positive_money_flow.rolling(window=period).sum()

        rolling_negative_money_flow = negative_money_flow.rolling(window=period).sum()

        money_flow_ratio = (
            rolling_positive_money_flow / rolling_negative_money_flow.replace(0, pd.NA)
        )

        result["MFI"] = 100 - (100 / (1 + money_flow_ratio))

        result["MFI"] = result["MFI"].fillna(100)

        logger.info("MFI calculation completed successfully.")

        return result
