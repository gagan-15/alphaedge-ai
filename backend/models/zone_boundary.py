"""Canonical Demand/Supply zone-boundary models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BoundaryMode(Enum):
    """Supported ways to display the same detected zone."""

    BODY_TO_WICK = "BODY_TO_WICK"
    WICK_TO_WICK = "WICK_TO_WICK"
    EXCEPTIONAL = "EXCEPTIONAL"


class ExceptionalBoundarySource(Enum):
    """Candle group that supplied an approved exceptional distal."""

    LEG_IN = "LEG_IN"
    LEG_OUT = "LEG_OUT"


class BoundaryReasonCode(Enum):
    """Deterministic results emitted by boundary calculation/validation."""

    CANONICAL_BODY_TO_WICK = "CANONICAL_BODY_TO_WICK"
    ALTERNATE_WICK_TO_WICK = "ALTERNATE_WICK_TO_WICK"
    EXCEPTIONAL_LEG_IN_OVERLAP = "EXCEPTIONAL_LEG_IN_OVERLAP"
    EXCEPTIONAL_LEG_OUT_OVERLAP = "EXCEPTIONAL_LEG_OUT_OVERLAP"
    EXCEPTIONAL_NOT_QUALIFIED = "EXCEPTIONAL_NOT_QUALIFIED"
    MALFORMED_BOUNDARY = "MALFORMED_BOUNDARY"
    NON_POSITIVE_BOUNDARY = "NON_POSITIVE_BOUNDARY"
    INVERTED_BOUNDARY = "INVERTED_BOUNDARY"
    ZERO_WIDTH_BOUNDARY = "ZERO_WIDTH_BOUNDARY"


@dataclass(frozen=True)
class BoundarySet:
    """One proximal/distal representation of a zone."""

    proximal: float
    distal: float
    mode: BoundaryMode
    exceptional_source: ExceptionalBoundarySource | None = None


@dataclass(frozen=True)
class ZoneBoundaryResult:
    """Canonical, alternate and selected boundaries for one zone identity."""

    standard: BoundarySet
    wick_to_wick: BoundarySet
    selected: BoundarySet
    exceptional: BoundarySet | None = None
    reason_codes: tuple[BoundaryReasonCode, ...] = ()

    @property
    def uses_exceptional_boundary(self) -> bool:
        return self.selected.mode == BoundaryMode.EXCEPTIONAL
