"""
Departure Detector for AlphaEdge AI.

Sprint:
    2.26 - Zone Detection Engine

Purpose:
    Detect whether price leaves a BaseRegion with
    sufficient strength to qualify as a valid departure.
"""

from pandas import DataFrame

from backend.config.settings import (
    MIN_DEPARTURE_RANGE_MULTIPLIER,
)
from backend.core.candle_utils import CandleUtils
from backend.core.logger import logger
from backend.models.base_region import BaseRegion
from backend.models.departure import (
    Departure,
    DepartureDirection,
)


class DepartureDetector:
    """
    Detect valid departures from a BaseRegion.
    """

    REQUIRED_COLUMNS = (
        "Open",
        "High",
        "Low",
        "Close",
    )

    def detect(
        self,
        market_data: DataFrame,
        base: BaseRegion,
    ) -> Departure | None:
        """
        Detect a valid departure immediately
        after a BaseRegion.

        Returns:
            Departure if detected.
            None otherwise.
        """

        logger.info("Starting departure detection.")

        self._validate_input(
            market_data,
            base,
        )

        departure_index = base.end_index + 1

        if departure_index >= len(market_data):
            logger.info("No candle exists after base.")
            return None

        departure_candle = market_data.iloc[departure_index]

        base_data = market_data.iloc[base.start_index : base.end_index + 1]

        base_high = float(base_data["High"].max())

        base_low = float(base_data["Low"].min())

        average_base_range = self._calculate_average_base_range(base_data)

        departure_range = CandleUtils.calculate_range(
            high_price=float(departure_candle["High"]),
            low_price=float(departure_candle["Low"]),
        )

        previous_candle = market_data.iloc[departure_index - 1]
        gap_up_size = max(
            0.0,
            float(departure_candle["Low"]) - float(previous_candle["High"]),
        )
        gap_down_size = max(
            0.0,
            float(previous_candle["Low"]) - float(departure_candle["High"]),
        )
        gap_impulse = max(gap_up_size, gap_down_size)
        strong_gap = gap_impulse >= average_base_range * 0.5

        if (
            departure_range
            < average_base_range * MIN_DEPARTURE_RANGE_MULTIPLIER
            and not strong_gap
        ):
            logger.info("Departure rejected. " "Range too small.")
            return None

        open_price = float(departure_candle["Open"])

        close_price = float(departure_candle["Close"])

        if not self._leg_out_is_stronger(
            market_data,
            base,
            departure_index,
        ):
            logger.info(
                "Departure rejected. Leg-out is not stronger than leg-in "
                "or lacks directional follow-through."
            )
            return None

        if (
            (
                CandleUtils.is_bullish(
                    open_price,
                    close_price,
                )
                or gap_up_size > 0
            )
            and close_price > base_high
        ):
            logger.info("Bullish departure detected.")

            return Departure(
                direction=DepartureDirection.BULLISH,
                departure_index=departure_index,
            )

        if (
            (
                CandleUtils.is_bearish(
                    open_price,
                    close_price,
                )
                or gap_down_size > 0
            )
            and close_price < base_low
        ):
            logger.info("Bearish departure detected.")

            return Departure(
                direction=DepartureDirection.BEARISH,
                departure_index=departure_index,
            )

        logger.info("No valid departure found.")

        return None

    @staticmethod
    def _leg_out_is_stronger(
        market_data: DataFrame,
        base: BaseRegion,
        departure_index: int,
    ) -> bool:
        """Compare the departure with the candle immediately before the base."""

        if base.start_index == 0:
            return False

        leg_in = market_data.iloc[base.start_index - 1]
        departure = market_data.iloc[departure_index]
        leg_in_body = abs(float(leg_in["Close"]) - float(leg_in["Open"]))
        leg_out_body = abs(float(departure["Close"]) - float(departure["Open"]))
        previous_close = float(market_data.iloc[departure_index - 1]["Close"])
        effective_impulse = max(
            leg_out_body,
            abs(float(departure["Open"]) - previous_close),
            abs(float(departure["Close"]) - previous_close),
        )

        if leg_in_body <= 0 or effective_impulse < leg_in_body * 1.1:
            return False

        base_data = market_data.iloc[base.start_index : base.end_index + 1]
        base_high = float(base_data["High"].max())
        base_low = float(base_data["Low"].min())
        if float(departure["Close"]) > base_high:
            direction = 1.0
        elif float(departure["Close"]) < base_low:
            direction = -1.0
        else:
            return False
        follow_through = market_data.iloc[
            departure_index : min(departure_index + 3, len(market_data))
        ]
        if len(follow_through) < 2:
            return False

        final_close = float(follow_through.iloc[-1]["Close"])
        directional_move = direction * (
            final_close - float(departure["Open"])
        )

        zone_width = max(base_high - base_low, 1e-9)

        if direction > 0:
            closes_outside = int((follow_through["Close"] > base_high).sum())
            sustained_move = final_close - base_high
        else:
            closes_outside = int((follow_through["Close"] < base_low).sum())
            sustained_move = base_low - final_close

        return (
            directional_move > leg_in_body
            and closes_outside >= 2
            and sustained_move >= zone_width * 1.5
        )

    @staticmethod
    def _calculate_average_base_range(
        base_data: DataFrame,
    ) -> float:
        """
        Calculate the average range of all
        candles inside the BaseRegion.

        Args:
            base_data:
                DataFrame containing only
                base candles.

        Returns:
            Average candle range.
        """

        total_range = 0.0

        for _, candle in base_data.iterrows():

            total_range += CandleUtils.calculate_range(
                high_price=float(candle["High"]),
                low_price=float(candle["Low"]),
            )

        return total_range / len(base_data)

    @classmethod
    def _validate_input(
        cls,
        market_data: DataFrame,
        base: BaseRegion,
    ) -> None:
        """
        Validate DepartureDetector input.

        Args:
            market_data:
                Validated OHLCV data.

            base:
                BaseRegion to evaluate.

        Raises:
            TypeError:
                If market_data or base
                are invalid.

            ValueError:
                If required columns
                are missing.
        """

        if not isinstance(
            market_data,
            DataFrame,
        ):
            raise TypeError("Market data must be a pandas DataFrame.")

        if not isinstance(
            base,
            BaseRegion,
        ):
            raise TypeError("base must be a BaseRegion.")

        if market_data.empty:
            raise ValueError("Market data cannot be empty.")

        missing_columns = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in market_data.columns
        ]

        if missing_columns:
            raise ValueError(
                "Market data is missing required columns: " + ", ".join(missing_columns)
            )

        if base.start_index >= len(market_data):
            raise ValueError("Base start index is outside market data.")

        if base.end_index >= len(market_data):
            raise ValueError("Base end index is outside market data.")

        logger.info("Departure detector input validation completed.")
