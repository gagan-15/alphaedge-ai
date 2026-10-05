"""
Multi-Timeframe Engine.

Sprint:
    2.32 - Multi-Timeframe Engine
"""

from pandas import DataFrame

from backend.config.multi_timeframe_config import (
    MultiTimeframeConfig,
)
from backend.engines.demand_supply_engine.market_structure_engine import (
    MarketStructureEngine,
)
from backend.models.market_structure.market_structure_state import (
    StructureTrend,
)
from backend.models.multi_timeframe.multi_timeframe_request import (
    MultiTimeframeRequest,
)
from backend.models.multi_timeframe.multi_timeframe_result import (
    MultiTimeframeResult,
)
from backend.validators.multi_timeframe_validator import (
    MultiTimeframeValidator,
)


class MultiTimeframeEngine:
    """
    Analyze multiple timeframes.
    """

    def __init__(
        self,
        config: MultiTimeframeConfig | None = None,
    ) -> None:

        self._config = config or MultiTimeframeConfig()

        self._market_structure = (
            MarketStructureEngine()
        )

    def analyze(
        self,
        request: MultiTimeframeRequest,
        market_data: dict[str, DataFrame],
    ) -> MultiTimeframeResult:

        MultiTimeframeValidator.validate(
            request,
            self._config,
        )

        results = {}

        for timeframe in request.timeframes:

            results[timeframe] = (
                self._market_structure.analyze(
                    market_data[timeframe],
                )
            )

        aligned = self._resolve_alignment(
            results,
        )

        return MultiTimeframeResult(
            timeframe_results=results,
            primary_timeframe=request.primary_timeframe,
            aligned_trend=aligned,
            is_aligned=(
                aligned
                != StructureTrend.SIDEWAYS
            ),
        )

    @staticmethod
    def _resolve_alignment(
        results,
    ) -> StructureTrend:

        trends = [
            result.state.trend
            for result in results.values()
        ]

        if all(
            trend == StructureTrend.BULLISH
            for trend in trends
        ):
            return StructureTrend.BULLISH

        if all(
            trend == StructureTrend.BEARISH
            for trend in trends
        ):
            return StructureTrend.BEARISH

        return StructureTrend.SIDEWAYS
