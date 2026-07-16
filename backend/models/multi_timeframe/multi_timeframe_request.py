"""
Multi-Timeframe Request model.

Sprint:
    2.32 - Multi-Timeframe Engine
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MultiTimeframeRequest:
    """
    Request for multi-timeframe analysis.
    """

    primary_timeframe: str

    timeframes: list[str] = field(
        default_factory=list,
    )

    @property
    def total_timeframes(
        self,
    ) -> int:
        """
        Return requested timeframe count.
        """

        return len(
            self.timeframes,
        )
