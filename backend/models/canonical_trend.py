"""Canonical GTF trend result models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CanonicalTrendState(str, Enum):
    """Deterministic states produced by the canonical GTF trend engine."""

    UPTREND = "UPTREND"
    DOWNTREND = "DOWNTREND"
    SIDEWAYS = "SIDEWAYS"
    UNAVAILABLE = "UNAVAILABLE"


class SmaColour(str, Enum):
    """Canonical D32 colour of the 50-period simple moving average."""

    GREEN = "GREEN"
    RED = "RED"
    NEUTRAL = "NEUTRAL"
    UNAVAILABLE = "UNAVAILABLE"


class TrendAlignment(str, Enum):
    """Informational relationship between an execution zone and Trend."""

    ALIGNED = "ALIGNED"
    OPPOSING = "OPPOSING"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class TrendReasonCode(str, Enum):
    """Explain why a canonical trend result is or is not available."""

    CANONICAL_GTF_TREND = "CANONICAL_GTF_TREND"
    NO_CANONICAL_TREND_TIMEFRAME = "NO_CANONICAL_TREND_TIMEFRAME"
    NO_VALID_DATA_SEGMENT = "NO_VALID_DATA_SEGMENT"
    NO_COMPLETED_CANDLES = "NO_COMPLETED_CANDLES"
    INSUFFICIENT_CONSECUTIVE_HISTORY = "INSUFFICIENT_CONSECUTIVE_HISTORY"
    INVALID_CANDLE_DATA = "INVALID_CANDLE_DATA"
    ATR_UNAVAILABLE = "ATR_UNAVAILABLE"
    ZERO_ATR = "ZERO_ATR"
    MARKET_DATA_UNAVAILABLE = "MARKET_DATA_UNAVAILABLE"


@dataclass(frozen=True)
class CanonicalTrendResult:
    """Immutable evidence returned by the canonical GTF trend engine."""

    symbol: str
    trend_timeframe: str | None
    trend_state: CanonicalTrendState
    sma50_current: float | None
    sma50_seven_bars_ago: float | None
    sma_colour: SmaColour
    atr14: float | None
    normalized_slope: float | None
    trend_angle_degrees: float | None
    evaluation_timestamp: datetime | None
    data_sufficient: bool
    reason_codes: tuple[TrendReasonCode, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-safe representation without recalculating evidence."""

        return {
            "symbol": self.symbol,
            "trend_timeframe": self.trend_timeframe,
            "trend_state": self.trend_state.value,
            "sma50_current": self.sma50_current,
            "sma50_seven_bars_ago": self.sma50_seven_bars_ago,
            "sma_colour": self.sma_colour.value,
            "atr14": self.atr14,
            "normalized_slope": self.normalized_slope,
            "trend_angle_degrees": self.trend_angle_degrees,
            "evaluation_timestamp": (
                self.evaluation_timestamp.isoformat()
                if self.evaluation_timestamp is not None
                else None
            ),
            "data_sufficient": self.data_sufficient,
            "reason_codes": [reason.value for reason in self.reason_codes],
        }
