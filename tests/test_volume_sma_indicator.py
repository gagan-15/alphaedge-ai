"""
File Name:
    test_volume_sma_indicator.py

Purpose:
    Unit tests for the Volume SMA Indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.volume_sma_indicator import VolumeSMAIndicator


def test_volume_sma_indicator_creates_column():
    """
    Test that Volume SMA calculation creates
    the expected Volume SMA column.
    """

    data = pd.DataFrame(
        {
            "Volume": list(range(100, 130))
        }
    )

    indicator = VolumeSMAIndicator()

    result = indicator.calculate(data)

    assert "Volume_SMA_20" in result.columns