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
from backend.indicators.macd_indicator import MACDIndicator
from backend.indicators.atr_indicator import ATRIndicator
from backend.indicators.bollinger_bands_indicator import BollingerBandsIndicator
from backend.indicators.volume_sma_indicator import VolumeSMAIndicator


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
        self.volume_sma_indicator = VolumeSMAIndicator()

    def calculate_sma(self, data, period=20):
        """
        Calculate the Simple Moving Average (SMA).
        """

        return self.sma_indicator.calculate(data, period)
    
    def calculate_volume_sma(self,data, period: int = 20):
            """
            Calculate the Volume Simple Moving Average.

            Args:
                data:
                    Market data.

                period:
                    Volume SMA period.

            Returns:
                pd.DataFrame
            """

            return self.volume_sma_indicator.calculate(
                data,
                period
            )
    
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
    
    @staticmethod
    def calculate_macd(
        data,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ):
        """
        Calculate MACD values.

        Args:
            data: Market data.
            fast_period: Fast EMA period.
            slow_period: Slow EMA period.
            signal_period: Signal EMA period.

        Returns:
            pd.DataFrame: MACD, Signal and Histogram.
        """

        indicator = MACDIndicator(
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period
        )

        return indicator.calculate(data)
    
    @staticmethod
    def calculate_atr(
        data,
        period: int = 14
    ):
        """
        Calculate Average True Range (ATR).

        Args:
            data: Market data.
            period: ATR period.

        Returns:
            pd.Series: ATR values.
        """

        indicator = ATRIndicator(period)

        return indicator.calculate(data)
    
    @staticmethod
    def calculate_bollinger_bands(
        data,
        period: int = 20,
        multiplier: int = 2
    ):
        """
        Calculate Bollinger Bands.

        Args:
            data: Market data.
            period: Moving average period.
            multiplier: Standard deviation multiplier.

        Returns:
            pd.DataFrame:
                Middle Band,
                Upper Band,
                Lower Band.
        """

        indicator = BollingerBandsIndicator(
            period=period,
            multiplier=multiplier
        )

        return indicator.calculate(data)