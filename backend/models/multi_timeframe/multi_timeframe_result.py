"""
Multi-Timeframe Result model.

Sprint:
    2.32 - Multi-Timeframe Engine
"""

from dataclasses import dataclass, field

from backend.models.market_structure.market_structure_result import (
    MarketStructureResult,
)
from backend.models.market_structure.market_structure_state import (
    StructureTrend,
)


@dataclass(frozen=True)
class MultiTimeframeResult:
    """
    Represents market structure analysis
    across multiple timeframes.
    """

    timeframe_results: dict[str, MarketStructureResult] = field(
        default_factory=dict,
    )

    primary_timeframe: str = ""

    aligned_trend: StructureTrend = StructureTrend.SIDEWAYS

    is_aligned: bool = False

    @property
    def total_timeframes(self) -> int:
        """
        Return analyzed timeframe count.
        """

        return len(self.timeframe_results)

    @property
    def primary_result(
        self,
    ) -> MarketStructureResult | None:
        """
        Return the primary timeframe result.
        """

        return self.timeframe_results.get(
            self.primary_timeframe,
        )

    def get_result(
        self,
        timeframe: str,
    ) -> MarketStructureResult | None:
        """
        Return result for a timeframe.
        """

        return self.timeframe_results.get(
            timeframe,
        )
