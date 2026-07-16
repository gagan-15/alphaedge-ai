"""
Change of Character (CHoCH) Engine.

Sprint:
    2.30 - Change of Character Engine
"""

from pandas import DataFrame

from backend.config.choch_config import CHoCHConfig
from backend.engines.demand_supply_engine.bos_detector import BOSDetector
from backend.engines.demand_supply_engine.structure_trend_resolver import (
    StructureTrendResolver,
)
from backend.engines.demand_supply_engine.swing_detector import SwingDetector
from backend.models.bos_result import BOSDirection
from backend.models.choch_result import CHoCHResult
from backend.validators.choch_validator import CHoCHValidator
from .choch_detector import CHoCHDetector
from backend.config.bos_config import BOSConfig


class CHoCHEngine:
    """
    Detect Change of Character events.
    """

    def __init__(
        self,
        config: CHoCHConfig | None = None,
    ) -> None:

        self._config = config or CHoCHConfig()

        self._validator = CHoCHValidator()

        self._swing_detector = SwingDetector(
            BOSConfig(
                swing_left_bars=2,
                swing_right_bars=2,
                confirmation_source=self._config.confirmation_source,
                break_buffer_type=self._config.break_buffer_type,
                break_buffer_value=self._config.break_buffer_value,
                allow_equal_break=self._config.allow_equal_break,
            )
        )

        self._trend_resolver = StructureTrendResolver()

        self._bos_detector = BOSDetector(
            BOSConfig(
                confirmation_source=self._config.confirmation_source,
                break_buffer_type=self._config.break_buffer_type,
                break_buffer_value=self._config.break_buffer_value,
                allow_equal_break=self._config.allow_equal_break,
            )
        )

        self._choch_detector = CHoCHDetector()

    def detect(
        self,
        market_data: DataFrame,
    ) -> CHoCHResult:
        """
        Detect CHoCH events.
        """

        self._validator.validate_market_data(
            market_data,
        )

        self._validator.validate_config(
            self._config,
        )

        swings = self._swing_detector.detect(
            market_data,
        )

        trend = self._trend_resolver.resolve(
            swings,
        )

        bos_events = self._bos_detector.detect(
            market_data,
            swings,
        )

        choch_events = self._choch_detector.detect(
            trend,
            bos_events,
        )

        bullish = [
            event for event in choch_events if event.direction == BOSDirection.BULLISH
        ]

        bearish = [
            event for event in choch_events if event.direction == BOSDirection.BEARISH
        ]

        return CHoCHResult(
            has_choch=bool(choch_events),
            has_bullish_choch=bool(bullish),
            has_bearish_choch=bool(bearish),
            latest_event=choch_events[-1] if choch_events else None,
            latest_bullish_event=bullish[-1] if bullish else None,
            latest_bearish_event=bearish[-1] if bearish else None,
            bullish_events=len(bullish),
            bearish_events=len(bearish),
            total_events=len(choch_events),
            swings_evaluated=len(swings),
        )
