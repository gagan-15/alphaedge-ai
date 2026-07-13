"""
Base Region model for AlphaEdge AI.

Sprint:
    2.26 - Zone Detection Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BaseRegion:
    """
    Represents a detected group of consecutive base candles.

    Attributes:
        start_index:
            Positional index of the first candle in the base.

        end_index:
            Positional index of the final candle in the base.

    Raises:
        ValueError:
            If either index is negative or the end index is before
            the start index.
    """

    start_index: int
    end_index: int

    def __post_init__(self) -> None:
        """
        Validate the base-region boundaries.

        Raises:
            ValueError:
                If the indexes do not represent a valid region.
        """

        if self.start_index < 0:
            raise ValueError("Base start index cannot be negative.")

        if self.end_index < 0:
            raise ValueError("Base end index cannot be negative.")

        if self.end_index < self.start_index:
            raise ValueError("Base end index cannot be before start index.")

    @property
    def candle_count(self) -> int:
        """
        Return the number of candles inside the base.

        Returns:
            Number of candles in the detected base.
        """

        return self.end_index - self.start_index + 1
