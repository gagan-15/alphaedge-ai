import pandas as pd
import pytest

from backend.indicators.macd_indicator import MACDIndicator

def test_macd_calculation():
    """
    Test successful MACD calculation.
    """

    data = pd.DataFrame({
        "Close": [
            100,101,102,103,104,105,106,107,108,109,
            110,111,112,113,114,115,116,117,118,119,
            120,121,122,123,124,125,126,127,128,129,
            130,131,132,133,134
        ]
    })

    indicator = MACDIndicator()

    result = indicator.calculate(data)

    assert isinstance(result, pd.DataFrame)

    assert "MACD" in result.columns
    assert "Signal" in result.columns
    assert "Histogram" in result.columns

    assert len(result) == len(data)