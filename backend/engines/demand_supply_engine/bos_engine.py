"""
Break Of Structure Engine for AlphaEdge AI.

Sprint:
    2.29 - Break of Structure Engine
"""

from pandas import DataFrame

from backend.config.bos_config import BOSConfig
from backend.core.logger import logger
from backend.engines.demand_supply_engine.bos_detector import (
    BOSDetector,
)
from backend.engines.demand_supply_engine.swing_detector import (
    SwingDetector,
)
from backend.validators.bos_validator import BOSValidator

from backend.models.bos_result import (
    BOSResult,
    BOSDirection,
)


class BOSEngine:
    """
    Orchestrates the complete
    Break Of Structure workflow.

    Responsibilities

    1. Validate inputs
    2. Detect swings
    3. Detect BOS
    4. Return BOSResult
    """

    def __init__(
        self,
        config: BOSConfig | None = None,
    ) -> None:

        self._config = config or BOSConfig()

        self._swing_detector = SwingDetector(
            self._config
        )

        self._bos_detector = BOSDetector(
            self._config
        )

    def detect(
        self,
        market_data: DataFrame,
    ) -> BOSResult:
        """
        Detect Break Of Structure.
        """

        logger.info(
            "Starting Break Of Structure detection."
        )

        BOSValidator.validate(
            market_data,
            self._config,
        )

        swings = self._swing_detector.detect(
            market_data
        )

        events = self._bos_detector.detect(
            market_data,
            swings,
        )

        bullish = [
            event
            for event in events
            if event.direction == BOSDirection.BULLISH
        ]

        bearish = [
            event
            for event in events
            if event.direction == BOSDirection.BEARISH
        ]

        logger.info(
            "%d BOS event(s) found.",
            len(events),
        )

        return BOSResult(
            events=events,
            swings_evaluated=len(swings),
            bullish_events=len(bullish),
            bearish_events=len(bearish),
            latest_bullish_event=(
                bullish[-1]
                if bullish
                else None
            ),
            latest_bearish_event=(
                bearish[-1]
                if bearish
                else None
            ),
        )