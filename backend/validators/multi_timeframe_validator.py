"""
Multi-Timeframe Validator.

Sprint:
    2.32 - Multi-Timeframe Engine
"""

from backend.config.multi_timeframe_config import (
    MultiTimeframeConfig,
)
from backend.models.multi_timeframe.multi_timeframe_request import (
    MultiTimeframeRequest,
)


class MultiTimeframeValidator:
    """
    Validate multi-timeframe inputs.
    """

    @staticmethod
    def validate(
        request: MultiTimeframeRequest,
        config: MultiTimeframeConfig,
    ) -> None:

        if not request.primary_timeframe:
            raise ValueError("primary_timeframe cannot be empty.")

        if not request.timeframes:
            raise ValueError("timeframes cannot be empty.")

        if request.primary_timeframe not in request.timeframes:
            raise ValueError("primary_timeframe must exist in timeframes.")

        if config.minimum_aligned_timeframes < 1:
            raise ValueError("minimum_aligned_timeframes must be greater than zero.")
