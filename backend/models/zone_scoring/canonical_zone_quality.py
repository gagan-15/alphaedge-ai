"""Result models for the AlphaEdge Canonical Zone Quality Score."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneQualityContext:
    """Canonical downstream facts supplied without re-detecting formation."""

    lifecycle_status: str | None = None
    is_fresh: bool | None = None
    penetration_percent: float | None = None
    max_penetration_percent: float | None = None
    authenticity_status: str | None = None


@dataclass(frozen=True)
class ZoneQualityComponent:
    """One independently auditable score component."""

    key: str
    score: float
    maximum_score: float
    evidence: tuple[str, ...]
    reason_codes: tuple[str, ...]
