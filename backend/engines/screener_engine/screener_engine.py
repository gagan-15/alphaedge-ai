"""
Screener Engine.

Sprint:
    2.39 - Screener Engine
"""

from backend.config.screener_config import (
    ScreenerConfig,
)
from backend.models.screener.screened_opportunity import (
    ScreenedOpportunity,
)
from backend.models.screener.screener_result import (
    ScreenerResult,
)
from backend.validators.screener_validator import (
    ScreenerValidator,
)


class ScreenerEngine:
    """
    Produces screener results from approved
    trading opportunities.
    """

    def __init__(
        self,
        config: ScreenerConfig,
    ) -> None:
        """
        Initialize the Screener Engine.
        """
        ScreenerValidator.validate_config(config)

        self._config = config

    def screen(
        self,
        opportunities: list[ScreenedOpportunity],
    ) -> ScreenerResult:
        """
        Produce a ScreenerResult from screened
        opportunities.
        """

        screened_opportunities = opportunities

        if self._config.approved_trades_only:
            screened_opportunities = [
                opportunity
                for opportunity in opportunities
                if opportunity.risk_management_result.approved
            ]

        return ScreenerResult(
            opportunities=screened_opportunities[: self._config.maximum_results],
        )
