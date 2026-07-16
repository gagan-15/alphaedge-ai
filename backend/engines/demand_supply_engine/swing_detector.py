"""
Swing Detector for AlphaEdge AI.

Sprint:
    2.29 - Break of Structure Engine
"""

from pandas import DataFrame

from backend.config.bos_config import BOSConfig
from backend.core.logger import logger
from backend.models.swing_point import (
    SwingPoint,
    SwingType,
)
from backend.validators.bos_validator import BOSValidator


class SwingDetector:
    """
    Detect confirmed swing highs
    and swing lows.
    """

    def __init__(
        self,
        config: BOSConfig,
    ) -> None:

        self._config = config

    def detect(
        self,
        market_data: DataFrame,
    ) -> list[SwingPoint]:
        """
        Detect confirmed swing points.
        """

        logger.info("Starting swing detection.")

        BOSValidator.validate(
            market_data,
            self._config,
        )

        swings: list[SwingPoint] = []

        left = self._config.swing_left_bars
        right = self._config.swing_right_bars

        for index in range(
            left,
            len(market_data) - right,
        ):

            if self._is_swing_high(
                market_data,
                index,
            ):

                swings.append(
                    SwingPoint(
                        index=index,
                        price=float(
                            market_data.iloc[index]["High"]
                        ),
                        swing_type=SwingType.HIGH,
                        confirmation_index=index + right,
                    )
                )

            elif self._is_swing_low(
                market_data,
                index,
            ):

                swings.append(
                    SwingPoint(
                        index=index,
                        price=float(
                            market_data.iloc[index]["Low"]
                        ),
                        swing_type=SwingType.LOW,
                        confirmation_index=index + right,
                    )
                )

        logger.info(
            "%d swing point(s) detected.",
            len(swings),
        )

        return swings

    def _is_swing_high(
        self,
        market_data: DataFrame,
        index: int,
    ) -> bool:

        current = float(
            market_data.iloc[index]["High"]
        )

        left = self._config.swing_left_bars
        right = self._config.swing_right_bars

        for i in range(
            index - left,
            index + right + 1,
        ):

            if i == index:
                continue

            if (
                float(
                    market_data.iloc[i]["High"]
                )
                >= current
            ):
                return False

        return True

    def _is_swing_low(
        self,
        market_data: DataFrame,
        index: int,
    ) -> bool:

        current = float(
            market_data.iloc[index]["Low"]
        )

        left = self._config.swing_left_bars
        right = self._config.swing_right_bars

        for i in range(
            index - left,
            index + right + 1,
        ):

            if i == index:
                continue

            if (
                float(
                    market_data.iloc[i]["Low"]
                )
                <= current
            ):
                return False

        return True