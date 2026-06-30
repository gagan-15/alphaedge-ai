"""
File Name:
    indicator_service.py

Purpose:
    Provide a centralized service for calculating
    technical indicators.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

from backend.indicators.sma_indicator import SMAIndicator
from backend.indicators.ema_indicator import EMAIndicator
from backend.indicators.rsi_indicator import RSIIndicator


class IndicatorService:
    """
    Service responsible for managing
    technical indicator calculations.
    """

    def __init__(self):
        """
        Initialize the Indicator Service.
        """

        self.sma_indicator = SMAIndicator()
        self.ema_indicator = EMAIndicator()

    def calculate_sma(self, data, period=20):
        """
        Calculate the Simple Moving Average (SMA).
        """

        return self.sma_indicator.calculate(data, period)
    
    def calculate_ema(self, data, period=20):
        """
        Calculate the Exponential Moving Average (EMA).
        """

        return self.ema_indicator.calculate(data, period)
    
    def calculate_rsi( self, data, period: int = 14):
        """
        Calculate RSI.

        Args:
            data: Market data.
            period: RSI period.

        Returns:
            pd.Series
        """

        indicator = RSIIndicator(period)

        return indicator.calculate(data)