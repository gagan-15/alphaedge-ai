"""Canonical zone-authenticity models and relationship metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.models.zone import Zone


class AuthenticityStatus(Enum):
    """Canonical authenticity classification."""

    AUTHENTIC = "AUTHENTIC"
    NON_AUTHENTIC = "NON_AUTHENTIC"


class AuthenticityReasonCode(Enum):
    """Stable reason codes for authenticity decisions."""

    ORIGINAL = "ORIGINAL"
    REACTION = "REACTION"
    DUPLICATE = "DUPLICATE"
    NESTED = "NESTED"
    OVERLAPPING = "OVERLAPPING"


class ZoneRelationshipType(Enum):
    """Relationships that do not merge or invalidate either zone."""

    REACTION_PARENT = "REACTION_PARENT"
    NESTED_PARENT = "NESTED_PARENT"
    NESTED_CHILD = "NESTED_CHILD"
    OVERLAPPING = "OVERLAPPING"
    DUPLICATE = "DUPLICATE"


class ReactionSource(Enum):
    """Observed part of the origin candle that reacted to a parent zone."""

    BODY = "BODY"
    WICK = "WICK"


@dataclass(frozen=True)
class FormationEvidence:
    """Formation indexes needed to evaluate Good Closing without redetection."""

    leg_in_start_index: int
    leg_in_end_index: int
    departure_index: int


@dataclass(frozen=True)
class ZoneRelationship:
    """One immutable relationship between two canonical zone identities."""

    relationship_type: ZoneRelationshipType
    related_zone_id: str
    overlap_percent: float | None = None


@dataclass(frozen=True)
class ZoneAuthenticityRecord:
    """Authenticity decision and evidence for one detected zone occurrence."""

    zone: Zone
    zone_id: str
    occurrence_id: str
    symbol: str
    timeframe: str
    status: AuthenticityStatus
    reason_code: AuthenticityReasonCode
    reason: str
    canonical_origin: str
    normalized_proximal: float
    normalized_distal: float
    parent_zone_id: str | None = None
    child_zone_ids: tuple[str, ...] = ()
    reaction_depth_percent: float | None = None
    reaction_timestamp: str | None = None
    reaction_source: ReactionSource | None = None
    duplicate_of_zone_id: str | None = None
    good_closing: bool | None = None
    relationships: tuple[ZoneRelationship, ...] = ()
