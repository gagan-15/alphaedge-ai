"""
File Name:
    test_cmf_indicator.py

Purpose:
    Unit tests for the CMF Indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.cmf_indicator import CMFIndicator


def test_cmf_indicator_creates_column():
    """
    Test that CMF calculation creates
    the expected CMF column.
    """

    data = pd.DataFrame(
        {
            "High": [110, 112, 115, 116, 118],
            "Low": [100, 102, 104, 105, 107],
            "Close": [108, 111, 114, 115, 117],
            "Volume": [1000, 1200, 1100, 1300, 1400],
        }
    )

    indicator = CMFIndicator()

    result = indicator.calculate(data, period=3)

    assert "CMF" in result.columns
