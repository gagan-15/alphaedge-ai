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
from backend.indicators.bollinger_bands_indicator import (
    BollingerBandsIndicator
)
from backend.indicators.volume_sma_indicator import (
    VolumeSMAIndicator
)
from backend.indicators.relative_volume_indicator import (
    RelativeVolumeIndicator
)
from backend.indicators.volume_confirmation_indicator import (
    VolumeConfirmationIndicator
)
from backend.indicators.vwap_indicator import VWAPIndicator
from backend.indicators.obv_indicator import OBVIndicator
from backend.indicators.cmf_indicator import CMFIndicator
from backend.indicators.mfi_indicator import MFIIndicator
from backend.indicators.adx_indicator import ADXIndicator
from backend.indicators.supertrend_indicator import SuperTrendIndicator
from backend.indicators.parabolic_sar_indicator import ParabolicSARIndicator
from backend.indicators.ichimoku_cloud_indicator import IchimokuCloudIndicator

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
        self.relative_volume_indicator = (
            RelativeVolumeIndicator()
        )
        self.volume_confirmation_indicator = (
            VolumeConfirmationIndicator()
        )
        self.vwap_indicator = VWAPIndicator()
        self.obv_indicator = OBVIndicator()
        self.cmf_indicator = CMFIndicator()
        self.mfi_indicator = MFIIndicator()
        self.adx_indicator = ADXIndicator()
        self.supertrend_indicator = SuperTrendIndicator()
        self.parabolic_sar_indicator = ParabolicSARIndicator()
        self.ichimoku_cloud_indicator = IchimokuCloudIndicator()

    def calculate_sma(
        self,
        data,
        period: int = 20
    ):
        """
        Calculate the Simple Moving Average (SMA).
        """

        return self.sma_indicator.calculate(
            data,
            period
        )

    def calculate_ema(
        self,
        data,
        period: int = 20
    ):
        """
        Calculate the Exponential Moving Average (EMA).
        """

        return self.ema_indicator.calculate(
            data,
            period
        )

    def calculate_volume_sma(
        self,
        data,
        period: int = 20
    ):
        """
        Calculate Volume SMA.
        """

        return self.volume_sma_indicator.calculate(
            data,
            period
        )

    def calculate_relative_volume(
        self,
        data,
        period: int = 20
    ):
        """
        Calculate Relative Volume (RVOL).
        """

        return self.relative_volume_indicator.calculate(
            data,
            period
        )

    def calculate_volume_confirmation(
        self,
        data,
        period: int = 20
    ):
        """
        Calculate Volume Confirmation.
        """

        return self.volume_confirmation_indicator.calculate(
            data,
            period
        )

    def calculate_vwap(
        self,
        data
    ):
        """
        Calculate Session VWAP.
        """

        return self.vwap_indicator.calculate(
            data
        )
    
    def calculate_cmf(
        self,
        data,
        period: int = 20
    ):
        """
        Calculate Chaikin Money Flow (CMF).

        Args:
            data:
                Market data.

            period:
                CMF calculation period.

        Returns:
            pd.DataFrame
        """

        return self.cmf_indicator.calculate(
            data,
            period
       )
    
    def calculate_adx(
    self,
    data,
    period: int = 14
):
        """
        Calculate Average Directional Index (ADX),
        Positive Directional Indicator (+DI),
        and Negative Directional Indicator (-DI).

        Args:
            data:
                Market data.

            period:
                ADX calculation period.

        Returns:
            pd.DataFrame
        """

        return self.adx_indicator.calculate(
            data,
            period
        )
        
    def calculate_mfi(
        self,
        data,
        period: int = 14
     ):
        """
        Calculate Money Flow Index (MFI).

        Args:
            data:
                Market data.

            period:
                MFI calculation period.

        Returns:
            pd.DataFrame
        """

        return self.mfi_indicator.calculate(
            data,
            period
        )
    
    def calculate_supertrend(
        self,
        data,
        period: int = 10,
        multiplier: float = 3.0
    ):
        """
        Calculate SuperTrend Indicator.
        """

        indicator = SuperTrendIndicator(
            period=period,
            multiplier=multiplier
        )

        return indicator.calculate(data)
    
    def calculate_parabolic_sar(
        self,
        data,
        acceleration: float = 0.02,
        maximum_acceleration: float = 0.20
    ):
        """
        Calculate Parabolic SAR Indicator.
        """

        indicator = ParabolicSARIndicator(
            acceleration=acceleration,
            maximum_acceleration=maximum_acceleration
        )

        return indicator.calculate(data)
    

    def calculate_ichimoku_cloud(
        self,
        data,
        conversion_period: int = 9,
        base_period: int = 26,
        leading_span_b_period: int = 52,
        displacement: int = 26
    ):
        """
        Calculate Ichimoku Cloud Indicator.
        """

        indicator = IchimokuCloudIndicator(
            conversion_period=conversion_period,
            base_period=base_period,
            leading_span_b_period=leading_span_b_period,
            displacement=displacement
        )

        return indicator.calculate(data)
            
    def calculate_obv(
        self,
        data
   ):
        """
        Calculate On-Balance Volume (OBV).

        Args:
            data:
                Market data.

        Returns:
            pd.DataFrame
        """

        return self.obv_indicator.calculate(data)

    def calculate_rsi(
        self,
        data,
        period: int = 14
    ):
        """
        Calculate RSI.
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
        Calculate MACD.
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
        """

        indicator = BollingerBandsIndicator(
            period=period,
            multiplier=multiplier
        )

        return indicator.calculate(data)
    

   