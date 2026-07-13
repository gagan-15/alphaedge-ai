"""
File Name:
    test_ema_indicator.py

Purpose:
    Unit tests for the EMA Indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.ema_indicator import EMAIndicator


def test_ema_indicator_creates_column():
    """
    Test that EMA calculation creates
    the expected EMA column.
    """

    data = pd.DataFrame({"Close": list(range(1, 31))})

    indicator = EMAIndicator()

    result = indicator.calculate(data)

    assert "EMA_20" in result.columns
