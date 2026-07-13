"""
Base Detector for AlphaEdge AI.

Sprint:
    2.26 - Zone Detection Engine

Purpose:
    Detect consecutive base candles from validated OHLCV
    market data.

A candle qualifies as a base candle when its real body is
less than or equal to the configured percentage of its
complete high-low range.
"""

from typing import Final

from pandas import DataFrame, Series

from backend.config.settings import (
    MAX_BASE_BODY_PERCENT,
    MAX_BASE_CANDLES,
    MIN_BASE_CANDLES,
)
from backend.core.logger import logger
from backend.models.base_region import BaseRegion
from backend.core.candle_utils import CandleUtils


class BaseDetector:
    """
    Detect valid base regions from OHLCV market data.

    The detector is responsible only for finding groups of
    consecutive base candles.

    It does not determine:

    - Demand or Supply
    - Leg-in direction
    - Leg-out direction
    - Zone boundaries
    - Zone freshness
    - Zone strength
    - Zone score
    """

    REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
        "Open",
        "High",
        "Low",
        "Close",
    )

    def detect(
        self,
        market_data: DataFrame,
    ) -> list[BaseRegion]:
        """
        Detect all valid base regions.

        Args:
            market_data:
                Validated OHLCV market data containing Open,
                High, Low and Close columns.

        Returns:
            A list of immutable BaseRegion objects.

        Raises:
            TypeError:
                If market_data is not a pandas DataFrame.

            ValueError:
                If market_data is empty, required columns are
                missing, or configuration values are invalid.
        """

        logger.info("Starting base detection.")

        self._validate_input(market_data)

        self._validate_configuration()

        detected_bases: list[BaseRegion] = []

        current_start_index: int | None = None

        for positional_index in range(len(market_data)):
            candle = market_data.iloc[positional_index]

            if self._is_base_candle(candle):
                if current_start_index is None:
                    current_start_index = positional_index

                continue

            if current_start_index is not None:
                self._append_region_if_valid(
                    detected_bases=detected_bases,
                    start_index=current_start_index,
                    end_index=positional_index - 1,
                )

                current_start_index = None

        # Close a base that continues until the final row.
        if current_start_index is not None:
            self._append_region_if_valid(
                detected_bases=detected_bases,
                start_index=current_start_index,
                end_index=len(market_data) - 1,
            )

        logger.info(
            "Base detection completed. "
            f"Detected {len(detected_bases)} valid base region(s)."
        )

        return detected_bases

    def _append_region_if_valid(
        self,
        detected_bases: list[BaseRegion],
        start_index: int,
        end_index: int,
    ) -> None:
        """
        Append a detected region when its candle count is valid.

        Args:
            detected_bases:
                Collection receiving valid BaseRegion objects.

            start_index:
                Positional index of the first base candle.

            end_index:
                Positional index of the last base candle.
        """

        candle_count = end_index - start_index + 1

        if MIN_BASE_CANDLES <= candle_count <= MAX_BASE_CANDLES:
            detected_bases.append(
                BaseRegion(
                    start_index=start_index,
                    end_index=end_index,
                )
            )

            logger.info(
                "Valid base region detected. "
                f"Start index: {start_index}, "
                f"end index: {end_index}, "
                f"candle count: {candle_count}."
            )

            return

        logger.info(
            "Base region rejected because candle count "
            "is outside the configured range. "
            f"Start index: {start_index}, "
            f"end index: {end_index}, "
            f"candle count: {candle_count}."
        )

    def _is_base_candle(
        self,
        candle: Series,
    ) -> bool:
        """
        Determine whether one candle qualifies
        as a base candle.
        """

        return CandleUtils.is_small_body(
            open_price=float(candle["Open"]),
            high_price=float(candle["High"]),
            low_price=float(candle["Low"]),
            close_price=float(candle["Close"]),
        )

    @classmethod
    def _validate_input(
        cls,
        market_data: DataFrame,
    ) -> None:
        """
        Validate input required by the detector.

        Args:
            market_data:
                DataFrame supplied to base detection.

        Raises:
            TypeError:
                If market_data is not a DataFrame.

            ValueError:
                If the DataFrame is empty or required columns
                are missing.
        """

        if not isinstance(
            market_data,
            DataFrame,
        ):
            raise TypeError("Market data must be a pandas DataFrame.")

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

    @staticmethod
    def _validate_configuration() -> None:
        """
        Validate Base Detector configuration.

        Raises:
            ValueError:
                If configured candle counts or body percentage
                are invalid.
        """

        if MIN_BASE_CANDLES < 1:
            raise ValueError("MIN_BASE_CANDLES must be at least 1.")

        if MAX_BASE_CANDLES < MIN_BASE_CANDLES:
            raise ValueError(
                "MAX_BASE_CANDLES cannot be less than " "MIN_BASE_CANDLES."
            )

        if not (0.0 <= MAX_BASE_BODY_PERCENT <= 100.0):
            raise ValueError("MAX_BASE_BODY_PERCENT must be between " "0 and 100.")
