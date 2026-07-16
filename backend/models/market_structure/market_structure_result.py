"""
Market Structure Result.

Sprint:
    2.31 - Market Structure Engine
"""

from dataclasses import dataclass, field

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
    """

    state: StructureState

    structure_points: list[StructurePoint] = field(
        default_factory=list,
    )

    @property
    def latest_point(
        self,
    ) -> StructurePoint | None:
        """
        Return latest structure point.
        """

        if not self.structure_points:
            return None

        return self.structure_points[-1]

    @property
    def total_points(
        self,
    ) -> int:
        """
        Return total structure points.
        """

        return len(
            self.structure_points,
        )
