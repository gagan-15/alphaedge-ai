"""
File Name:
    test_sma_indicator.py

Purpose:
    Unit tests for the SMA Indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.sma_indicator import SMAIndicator


def test_sma_indicator_creates_column():
    """
    Test that SMA calculation creates
    the expected SMA column.
    """

    data = pd.DataFrame({"Close": list(range(1, 31))})

    indicator = SMAIndicator()

    result = indicator.calculate(data)

    assert "SMA_20" in result.columns
