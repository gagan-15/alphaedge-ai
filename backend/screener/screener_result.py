"""
Screener Result model.

Sprint:
    2.39 - Screener Engine
"""

from dataclasses import dataclass

from backend.models.risk_management.risk_management_result import (
    RiskManagementResult,
)


@dataclass(frozen=True)
class ScreenerResult:
    """
    Represents the result returned by the
    Screener Engine.
    """

    symbol: str

    risk_management_result: RiskManagementResult
