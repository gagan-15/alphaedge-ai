"""
File Name:
    test_obv_indicator.py

Purpose:
    Unit tests for the OBV Indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.obv_indicator import OBVIndicator


def test_obv_indicator_creates_column():
    """
    Test that OBV calculation creates
    the expected OBV column.
    """

    data = pd.DataFrame(
        {
            "Close": [100, 105, 103, 106],
            "Volume": [1000, 500, 700, 1000]
        }
    )

    indicator = OBVIndicator()

    result = indicator.calculate(data)

    assert "OBV" in result.columns