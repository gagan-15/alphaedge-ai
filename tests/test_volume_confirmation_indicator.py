"""
File Name:
    test_volume_confirmation_indicator.py

Purpose:
    Unit tests for the Volume Confirmation Indicator.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import pandas as pd

from backend.indicators.volume_confirmation_indicator import VolumeConfirmationIndicator


def test_volume_confirmation_indicator_creates_column():
    """
    Test that Volume Confirmation calculation
    creates the expected output column.
    """

    data = pd.DataFrame({"Volume": list(range(100, 130))})

    indicator = VolumeConfirmationIndicator()

    result = indicator.calculate(data)

    assert "Volume_Confirmation" in result.columns
