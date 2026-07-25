"""
Screened Opportunity model.

Sprint:
    2.39 - Screener Engine
"""

from dataclasses import dataclass

from backend.models.risk_management.risk_management_result import (
    RiskManagementResult,
)


@dataclass(frozen=True)
class ScreenedOpportunity:
    """
    Represents a single screened trading
    opportunity.
    """

    symbol: str

    risk_management_result: RiskManagementResult

    zone_type: str | None = None

    proximal_price: float | None = None

    distal_price: float | None = None

    zone_score: float | None = None

    distance_percent: float | None = None

    zone_fresh: bool | None = None

    touch_count: int | None = None

    base_index: int | None = None

    timeframe: str | None = None
