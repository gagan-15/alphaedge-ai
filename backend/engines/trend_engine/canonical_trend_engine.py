"""Canonical GTF 50-SMA seven-candle Trend Engine."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from math import atan, degrees, isfinite
from zoneinfo import ZoneInfo

import pandas as pd
from pandas import DataFrame

from backend.config.timeframe_hierarchy import TIMEFRAME_DURATION_MINUTES
from backend.models.canonical_trend import (
    CanonicalTrendResult,
    CanonicalTrendState,
    SmaColour,
    TrendAlignment,
    TrendReasonCode,
)

IST = ZoneInfo("Asia/Kolkata")
MINIMUM_HISTORY = 57
ANGLE_THRESHOLD_DEGREES = 5.0


class CanonicalTrendEngine:
    """Calculate canonical Trend only from approved D31/D32 evidence."""

    @staticmethod
    def wilder_atr(candles: DataFrame, period: int = 14) -> pd.Series:
        """Return standard True Range with Wilder-smoothed ATR."""

        high = pd.to_numeric(candles["High"], errors="coerce")
        low = pd.to_numeric(candles["Low"], errors="coerce")
        close = pd.to_numeric(candles["Close"], errors="coerce")
        previous_close = close.shift(1)
        true_range = pd.concat(
            (
                high - low,
                (high - previous_close).abs(),
                (low - previous_close).abs(),
            ),
            axis=1,
        ).max(axis=1)
        atr = pd.Series(float("nan"), index=candles.index, dtype="float64")
        if len(true_range) < period:
            return atr
        atr.iloc[period - 1] = float(true_range.iloc[:period].mean())
        for index in range(period, len(true_range)):
            atr.iloc[index] = (
                float(atr.iloc[index - 1]) * (period - 1)
                + float(true_range.iloc[index])
            ) / period
        return atr

    @staticmethod
    def classify_angle(angle_degrees: float) -> CanonicalTrendState:
        """Apply the approved strict five-degree D31 boundaries."""

        if angle_degrees > ANGLE_THRESHOLD_DEGREES:
            return CanonicalTrendState.UPTREND
        if angle_degrees < -ANGLE_THRESHOLD_DEGREES:
            return CanonicalTrendState.DOWNTREND
        return CanonicalTrendState.SIDEWAYS

    @staticmethod
    def alignment(zone_type: str, state: CanonicalTrendState) -> TrendAlignment:
        """Return informational execution-zone alignment only."""

        normalized = zone_type.strip().upper()
        if state == CanonicalTrendState.SIDEWAYS:
            return TrendAlignment.NEUTRAL
        if state == CanonicalTrendState.UNAVAILABLE:
            return TrendAlignment.UNKNOWN
        aligned = (
            normalized == "DEMAND" and state == CanonicalTrendState.UPTREND
        ) or (
            normalized == "SUPPLY" and state == CanonicalTrendState.DOWNTREND
        )
        return TrendAlignment.ALIGNED if aligned else TrendAlignment.OPPOSING

    def evaluate_segments(
        self,
        symbol: str,
        trend_timeframe: str | None,
        segments: tuple[DataFrame, ...],
        *,
        evaluated_at: datetime | None = None,
    ) -> CanonicalTrendResult:
        """Evaluate only the latest continuous valid market-data segment."""

        if trend_timeframe is None:
            return self.unavailable(
                symbol,
                None,
                TrendReasonCode.NO_CANONICAL_TREND_TIMEFRAME,
            )
        valid_segments = tuple(segment for segment in segments if not segment.empty)
        if not valid_segments:
            return self.unavailable(
                symbol,
                trend_timeframe,
                TrendReasonCode.NO_VALID_DATA_SEGMENT,
            )
        return self.evaluate(
            symbol,
            trend_timeframe,
            valid_segments[-1],
            evaluated_at=evaluated_at,
        )

    def evaluate(
        self,
        symbol: str,
        trend_timeframe: str | None,
        candles: DataFrame,
        *,
        evaluated_at: datetime | None = None,
    ) -> CanonicalTrendResult:
        """Calculate canonical GTF Trend from completed valid candles."""

        if trend_timeframe is None:
            return self.unavailable(
                symbol,
                None,
                TrendReasonCode.NO_CANONICAL_TREND_TIMEFRAME,
            )
        required = {"High", "Low", "Close"}
        if candles.empty:
            return self.unavailable(
                symbol,
                trend_timeframe,
                TrendReasonCode.NO_VALID_DATA_SEGMENT,
            )
        if not required.issubset(candles.columns):
            return self.unavailable(
                symbol,
                trend_timeframe,
                TrendReasonCode.INVALID_CANDLE_DATA,
            )

        completed = self.completed_candles(
            candles.sort_index(),
            trend_timeframe,
            evaluated_at=evaluated_at,
        )
        if completed.empty:
            return self.unavailable(
                symbol,
                trend_timeframe,
                TrendReasonCode.NO_COMPLETED_CANDLES,
            )
        numeric = completed[["High", "Low", "Close"]].apply(
            pd.to_numeric, errors="coerce"
        )
        if numeric.isna().any(axis=None) or not all(
            isfinite(float(value)) for value in numeric.to_numpy().flat
        ):
            return self.unavailable(
                symbol,
                trend_timeframe,
                TrendReasonCode.INVALID_CANDLE_DATA,
                completed.index[-1],
            )
        if len(completed) < MINIMUM_HISTORY:
            return self.unavailable(
                symbol,
                trend_timeframe,
                TrendReasonCode.INSUFFICIENT_CONSECUTIVE_HISTORY,
                completed.index[-1],
            )

        close = numeric["Close"]
        sma50 = close.rolling(window=50, min_periods=50).mean()
        current_sma = float(sma50.iloc[-1])
        earlier_sma = float(sma50.iloc[-8])
        atr = self.wilder_atr(numeric, 14)
        current_atr = float(atr.iloc[-1])
        if not isfinite(current_atr):
            return self.unavailable(
                symbol,
                trend_timeframe,
                TrendReasonCode.ATR_UNAVAILABLE,
                completed.index[-1],
            )
        if current_atr <= 0:
            return self.unavailable(
                symbol,
                trend_timeframe,
                TrendReasonCode.ZERO_ATR,
                completed.index[-1],
            )

        normalized_slope = (current_sma - earlier_sma) / (7 * current_atr)
        angle = degrees(atan(normalized_slope))
        colour = (
            SmaColour.GREEN
            if current_sma > earlier_sma
            else SmaColour.RED
            if current_sma < earlier_sma
            else SmaColour.NEUTRAL
        )
        timestamp = pd.Timestamp(completed.index[-1]).to_pydatetime()
        return CanonicalTrendResult(
            symbol=symbol.strip().upper(),
            trend_timeframe=trend_timeframe,
            trend_state=self.classify_angle(angle),
            sma50_current=current_sma,
            sma50_seven_bars_ago=earlier_sma,
            sma_colour=colour,
            atr14=current_atr,
            normalized_slope=normalized_slope,
            trend_angle_degrees=angle,
            evaluation_timestamp=timestamp,
            data_sufficient=True,
            reason_codes=(TrendReasonCode.CANONICAL_GTF_TREND,),
        )

    @staticmethod
    def completed_candles(
        candles: DataFrame,
        timeframe: str,
        *,
        evaluated_at: datetime | None = None,
    ) -> DataFrame:
        """Exclude the latest candle until its timeframe has completed."""

        now = evaluated_at or datetime.now(IST)
        if now.tzinfo is None:
            now = now.replace(tzinfo=IST)
        else:
            now = now.astimezone(IST)
        completed_positions: list[int] = []
        for position, raw_timestamp in enumerate(candles.index):
            timestamp = pd.Timestamp(raw_timestamp)
            local = (
                timestamp.tz_localize(IST)
                if timestamp.tzinfo is None
                else timestamp.tz_convert(IST)
            )
            if CanonicalTrendEngine._completion_time(local, timeframe) <= now:
                completed_positions.append(position)
        return candles.iloc[completed_positions]

    @staticmethod
    def _completion_time(timestamp: pd.Timestamp, timeframe: str) -> datetime:
        normalized = timeframe.strip()
        duration_key = normalized.upper()
        minutes = TIMEFRAME_DURATION_MINUTES.get(duration_key)
        if normalized.endswith("m") and normalized[:-1].isdigit():
            minutes = int(normalized[:-1])
        if normalized.endswith("H") and normalized[:-1].isdigit():
            minutes = int(normalized[:-1]) * 60
        if minutes is not None and minutes < 1_440:
            return timestamp.to_pydatetime() + timedelta(minutes=minutes)
        session_close = datetime.combine(
            timestamp.date(), time(15, 30), tzinfo=IST
        )
        return session_close

    @staticmethod
    def unavailable(
        symbol: str,
        trend_timeframe: str | None,
        reason: TrendReasonCode,
        evaluation_timestamp: object | None = None,
    ) -> CanonicalTrendResult:
        """Create one deterministic unavailable result."""

        timestamp = (
            pd.Timestamp(evaluation_timestamp).to_pydatetime()
            if evaluation_timestamp is not None
            else None
        )
        return CanonicalTrendResult(
            symbol=symbol.strip().upper(),
            trend_timeframe=trend_timeframe,
            trend_state=CanonicalTrendState.UNAVAILABLE,
            sma50_current=None,
            sma50_seven_bars_ago=None,
            sma_colour=SmaColour.UNAVAILABLE,
            atr14=None,
            normalized_slope=None,
            trend_angle_degrees=None,
            evaluation_timestamp=timestamp,
            data_sufficient=False,
            reason_codes=(reason,),
        )
