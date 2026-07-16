"""
Market Structure Result.

Sprint:
    2.30 - Market Structure Foundation
"""

from dataclasses import dataclass

from backend.models.market_structure.market_structure_point import (
    StructurePoint,
)
from backend.models.market_structure.market_structure_state import (
    StructureState,
)


@dataclass(frozen=True)
class MarketStructureResult:
    """
    Canonical market structure.

    This model represents only the
    current market structure.

    It does NOT know anything about:

    - BOS
    - CHoCH
    - Trend Engine
    - Liquidity

    Those engines consume this model.
    """

    state: StructureState

    structure_points: list[StructurePoint]
