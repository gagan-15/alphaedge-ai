"""
File Name:
    test_mfi_indicator.py

Purpose:
    Unit tests for the MFI Indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.mfi_indicator import MFIIndicator


def test_mfi_indicator_creates_column():
    """
    Test that MFI calculation creates
    the expected MFI column.
    """

    data = pd.DataFrame(
        {
            "High": [110, 112, 115, 116, 118],
            "Low": [100, 102, 104, 105, 107],
            "Close": [108, 111, 114, 115, 117],
            "Volume": [1000, 1200, 1100, 1300, 1400],
        }
    )

    indicator = MFIIndicator()

    result = indicator.calculate(data, period=3)

    assert "MFI" in result.columns
