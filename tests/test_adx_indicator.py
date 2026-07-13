"""
File Name:
    test_adx_indicator.py

Purpose:
    Unit tests for the ADX Indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.adx_indicator import ADXIndicator


def test_adx_indicator_creates_columns():
    """
    Test that ADX calculation creates
    the expected ADX, +DI and -DI columns.
    """

    data = pd.DataFrame(
        {
            "High": [110, 112, 115, 116, 118],
            "Low": [100, 102, 104, 105, 107],
            "Close": [108, 111, 114, 115, 117],
        }
    )

    indicator = ADXIndicator()

    result = indicator.calculate(data, period=3)

    assert "ADX" in result.columns

    assert "+DI" in result.columns

    assert "-DI" in result.columns
