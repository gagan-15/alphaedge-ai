"""Canonical price-leg evidence used by zone formation."""

from dataclasses import dataclass

from backend.models.departure import DepartureDirection


@dataclass(frozen=True)
class PriceLeg:
    """A maximal contiguous sequence of aligned exciting candles."""

    direction: DepartureDirection
    start_index: int
    end_index: int
    high: float
    low: float

    @property
    def candle_count(self) -> int:
        return self.end_index - self.start_index + 1
