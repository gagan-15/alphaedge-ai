"""
Multi-Timeframe Configuration.

Sprint:
    2.32 - Multi-Timeframe Engine
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MultiTimeframeConfig:
    """
    Configuration for multi-timeframe analysis.
    """

    primary_timeframe: str = "1D"

    timeframes: list[str] = field(
        default_factory=lambda: [
            "1W",
            "1D",
            "4H",
            "1H",
        ]
    )

    require_trend_alignment: bool = True

    minimum_aligned_timeframes: int = 2
