"""
Break Of Structure Detector for AlphaEdge AI.

Sprint:
    2.29 - Break of Structure Engine
"""

from pandas import DataFrame

from backend.config.bos_config import BOSConfig
from backend.core.logger import logger
from backend.models.bos_result import (
    BOSEvent,
    BOSDirection,
)
from backend.models.swing_point import (
    SwingPoint,
    SwingType,
)


class BOSDetector:
    """
    Detect bullish and bearish
    Break Of Structure events.
    """

    def __init__(
        self,
        config: BOSConfig,
    ) -> None:

        self._config = config

    def detect(
        self,
        market_data: DataFrame,
        swings: list[SwingPoint],
    ) -> list[BOSEvent]:
        """
        Detect Break Of Structure events.
        """

        logger.info("Starting BOS detection.")

        events: list[BOSEvent] = []

        broken_swings: set[int] = set()

        for swing in swings:

            if self._config.deduplicate_events and swing.index in broken_swings:
                continue

            event = self._detect_break(
                market_data,
                swing,
            )

            if event is None:
                continue

            events.append(event)

            broken_swings.add(swing.index)

        logger.info(
            "%d BOS event(s) detected.",
            len(events),
        )

        return events

    def _detect_break(
        self,
        market_data: DataFrame,
        swing: SwingPoint,
    ) -> BOSEvent | None:
        """
        Detect whether the supplied
        swing has been broken.
        """

        start = swing.confirmation_index + self._config.minimum_bars_after_swing

        for index in range(
            start,
            len(market_data),
        ):

            price = self._get_confirmation_price(
                market_data,
                index,
                swing.swing_type,
            )

            if swing.swing_type == SwingType.HIGH:

                if self._is_bullish_break(
                    price,
                    swing.price,
                ):

                    return self._create_event(
                        BOSDirection.BULLISH,
                        swing,
                        index,
                        price,
                    )

            else:

                if self._is_bearish_break(
                    price,
                    swing.price,
                ):

                    return self._create_event(
                        BOSDirection.BEARISH,
                        swing,
                        index,
                        price,
                    )

        return None

    def _is_bullish_break(
        self,
        price: float,
        swing_price: float,
    ) -> bool:

        required = self._apply_break_buffer(
            swing_price,
            bullish=True,
        )

        if self._config.allow_equal_break:
            return price >= required

        return price > required

    def _is_bearish_break(
        self,
        price: float,
        swing_price: float,
    ) -> bool:

        required = self._apply_break_buffer(
            swing_price,
            bullish=False,
        )

        if self._config.allow_equal_break:
            return price <= required

        return price < required

    def _create_event(
        self,
        direction: BOSDirection,
        swing: SwingPoint,
        break_index: int,
        break_price: float,
    ) -> BOSEvent:

        distance = abs(break_price - swing.price)

        percentage = (distance / swing.price) * 100

        return BOSEvent(
            direction=direction,
            break_index=break_index,
            break_price=break_price,
            broken_swing=swing,
            break_distance=distance,
            break_distance_percentage=percentage,
            confirmation_source=self._config.confirmation_source,
            is_confirmed=True,
            explanation=(
                f"{direction.value} BOS "
                f"{'above' if direction == BOSDirection.BULLISH else 'below'} "
                f"swing {swing.index}"
            ),
        )

    def _get_confirmation_price(
        self,
        market_data: DataFrame,
        index: int,
        swing_type: SwingType,
    ) -> float:
        """
        Return the configured
        confirmation price.
        """

        source = self._config.confirmation_source.lower()

        candle = market_data.iloc[index]

        if source == "close":
            return float(candle["Close"])

        if source == "high":
            return float(candle["High"])

        if source == "low":
            return float(candle["Low"])

        raise ValueError(f"Unsupported confirmation_source: {source}")

    def _apply_break_buffer(
        self,
        price: float,
        bullish: bool,
    ) -> float:
        """
        Apply configured break buffer.
        """

        buffer_value = self._config.break_buffer_value

        if self._config.break_buffer_type == "percentage":

            multiplier = 1 + buffer_value / 100 if bullish else 1 - buffer_value / 100

            return price * multiplier

        if self._config.break_buffer_type == "points":

            return price + buffer_value if bullish else price - buffer_value

        raise ValueError(
            f"Unsupported break_buffer_type: " f"{self._config.break_buffer_type}"
        )
