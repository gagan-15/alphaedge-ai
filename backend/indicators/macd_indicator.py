import logging
import pandas as pd
from backend.indicators.base_indicator import BaseIndicator
from backend.indicators.ema_indicator import EMAIndicator
from backend.validators.indicator_validator import IndicatorValidator


class MACDIndicator(BaseIndicator):
    """
    Moving Average Convergence Divergence (MACD) Indicator.

    Calculates:
    - MACD Line
    - Signal Line
    - Histogram
    """

    def __init__(
        self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9
    ):
        """
        Initialize the MACD Indicator.

        Args:
            fast_period (int): Fast EMA period.
            slow_period (int): Slow EMA period.
            signal_period (int): Signal EMA period.
        """

        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

        self.logger = logging.getLogger(__name__)

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD values.

        Args:
            data (pd.DataFrame): Market data containing the Close column.

        Returns:
            pd.DataFrame:
                MACD Line,
                Signal Line,
                Histogram.
        """

        IndicatorValidator.validate_common_input(data, self.slow_period)

        IndicatorValidator.validate_minimum_rows(data, self.slow_period)

        self.logger.info(
            "Starting MACD calculation " "(fast=%s, slow=%s, signal=%s)",
            self.fast_period,
            self.slow_period,
            self.signal_period,
        )

        fast_ema_indicator = EMAIndicator()
        slow_ema_indicator = EMAIndicator()

        fast_data = fast_ema_indicator.calculate(data.copy(), period=self.fast_period)

        slow_data = slow_ema_indicator.calculate(data.copy(), period=self.slow_period)

        fast_ema = fast_data[f"EMA_{self.fast_period}"]
        slow_ema = slow_data[f"EMA_{self.slow_period}"]

        macd_line = fast_ema - slow_ema

        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        histogram = macd_line - signal_line

        result = pd.DataFrame(
            {"MACD": macd_line, "Signal": signal_line, "Histogram": histogram}
        )

        self.logger.info("MACD calculation completed successfully.")

        return result
