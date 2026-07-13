import logging
import pandas as pd

from backend.indicators.base_indicator import BaseIndicator
from backend.validators.indicator_validator import IndicatorValidator


class RSIIndicator(BaseIndicator):
    """
    Relative Strength Index (RSI) Indicator.

    Calculates RSI using Wilder's smoothing method.
    """

    def __init__(self, period: int = 14):
        """
        Initialize the RSI Indicator.

        Args:
            period (int): RSI calculation period.
        """
        self.period = period
        self.logger = logging.getLogger(__name__)

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate RSI values.

        Args:
            data (pd.DataFrame): Market data containing the Close column.

        Returns:
            pd.Series: RSI values.
        """

        IndicatorValidator.validate_common_input(data, self.period)

        IndicatorValidator.validate_minimum_rows(data, self.period)

        self.logger.info("Starting RSI calculation with period=%s", self.period)

        # Extract closing prices
        close_prices = data["Close"]

        # Calculate price changes
        price_change = close_prices.diff()

        # Separate gains and losses
        gains = price_change.where(price_change > 0, 0.0)
        losses = -price_change.where(price_change < 0, 0.0)

        # Wilder's smoothing
        average_gain = gains.ewm(alpha=1 / self.period, adjust=False).mean()

        average_loss = losses.ewm(alpha=1 / self.period, adjust=False).mean()

        # Relative Strength
        relative_strength = average_gain / average_loss

        # RSI Formula
        rsi = 100 - (100 / (1 + relative_strength))

        # Handle edge cases
        rsi = rsi.fillna(0)

        self.logger.info("RSI calculation completed successfully.")

        return rsi
