"""
Screener Result model.

Sprint:
    2.39 - Screener Engine
"""

from dataclasses import dataclass

from backend.models.screener.screened_opportunity import (
    ScreenedOpportunity,
)


@dataclass(frozen=True)
class ScreenerResult:
    """
    Represents the complete output of the
    Screener Engine.
    """

    opportunities: list[ScreenedOpportunity]
