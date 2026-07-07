"""
File Name:
    test_relative_volume_indicator.py

Purpose:
    Unit tests for the Relative Volume (RVOL) Indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.relative_volume_indicator import (
    RelativeVolumeIndicator
)


def test_relative_volume_indicator_creates_column():
    """
    Test that Relative Volume calculation creates
    the expected RVOL column.
    """

    data = pd.DataFrame(
        {
            "Volume": list(range(100, 130))
        }
    )

    indicator = RelativeVolumeIndicator()

    result = indicator.calculate(data)

    assert "RVOL_20" in result.columns