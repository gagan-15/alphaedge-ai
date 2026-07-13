"""
Candle utility functions for AlphaEdge AI.

Sprint:
    2.26 - Zone Detection Engine
"""

from backend.config.settings import MAX_BASE_BODY_PERCENT


class CandleUtils:
    """
    Utility class containing reusable candle calculations.

    This class contains only generic candle mathematics.
    It does not contain any trading logic.
    """

    @staticmethod
    def calculate_body_size(
        open_price: float,
        close_price: float,
    ) -> float:
        """
        Calculate candle body size.
        """

        return abs(close_price - open_price)

    @staticmethod
    def calculate_range(
        high_price: float,
        low_price: float,
    ) -> float:
        """
        Calculate total candle range.
        """

        if high_price < low_price:
            raise ValueError("High price cannot be less than low price.")

        return high_price - low_price

    @classmethod
    def calculate_body_percentage(
        cls,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
    ) -> float:
        """
        Calculate candle body percentage.

        Formula:

        Body Size / Candle Range × 100
        """

        candle_range = cls.calculate_range(
            high_price,
            low_price,
        )

        if candle_range == 0:
            return 0.0

        body_size = cls.calculate_body_size(
            open_price,
            close_price,
        )

        return body_size / candle_range * 100.0

    @classmethod
    def is_small_body(
        cls,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
    ) -> bool:
        """
        Check whether a candle qualifies
        as a small-body candle.
        """

        body_percentage = cls.calculate_body_percentage(
            open_price,
            high_price,
            low_price,
            close_price,
        )

        return body_percentage <= MAX_BASE_BODY_PERCENT

    @staticmethod
    def is_bullish(
        open_price: float,
        close_price: float,
    ) -> bool:
        """
        Determine whether the candle is bullish.
        """

        return close_price > open_price

    @staticmethod
    def is_bearish(
        open_price: float,
        close_price: float,
    ) -> bool:
        """
        Determine whether the candle is bearish.
        """

        return close_price < open_price
