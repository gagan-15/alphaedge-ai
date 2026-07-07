"""
File Name:
    test_vwap_indicator.py

Purpose:
    Unit tests for the VWAP Indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.vwap_indicator import VWAPIndicator


def test_vwap_indicator_creates_column():
    """
    Test that VWAP calculation creates
    the expected VWAP column.
    """

    data = pd.DataFrame(
        {
            "High": list(range(110, 140)),
            "Low": list(range(100, 130)),
            "Close": list(range(105, 135)),
            "Volume": list(range(1000, 1030))
        }
    )

    indicator = VWAPIndicator()

    result = indicator.calculate(data)

    assert "VWAP" in result.columns