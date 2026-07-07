"""
File Name:
    cmf_indicator.py

Purpose:
    Calculate the Chaikin Money Flow (CMF) indicator.

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


class CMFIndicator(BaseIndicator):
    """
    Chaikin Money Flow (CMF) Indicator.
    """

    def calculate(
        self,
        data: pd.DataFrame,
        period: int = 20
    ) -> pd.DataFrame:
        """
        Calculate the Chaikin Money Flow (CMF).

        Args:
            data:
                Market data.

            period:
                CMF calculation period.

        Returns:
            pd.DataFrame:
                DataFrame containing the CMF column.
        """

        logger.info("Starting CMF calculation.")

        IndicatorValidator.validate_period(period)
        IndicatorValidator.validate_cmf_input(data)
        IndicatorValidator.validate_minimum_rows(
            data,
            period
        )

        result = data.copy()

        high_low_range = (
            result["High"] - result["Low"]
        )

        high_low_range = high_low_range.replace(
            0,
            pd.NA
        )

        money_flow_multiplier = (
            (
                (result["Close"] - result["Low"])
                -
                (result["High"] - result["Close"])
            )
            /
            high_low_range
        )

        money_flow_multiplier = (
            money_flow_multiplier.fillna(0)
        )

        money_flow_volume = (
            money_flow_multiplier
            *
            result["Volume"]
        )

        rolling_money_flow = (
            money_flow_volume.rolling(
                window=period
            ).sum()
        )

        rolling_volume = (
            result["Volume"]
            .rolling(window=period)
            .sum()
        )

        result["CMF"] = (
            rolling_money_flow
            /
            rolling_volume
        )

        logger.info(
            "CMF calculation completed successfully."
        )

        return result