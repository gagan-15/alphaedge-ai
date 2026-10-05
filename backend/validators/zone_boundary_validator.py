"""Validation for canonical Demand/Supply boundary calculations."""

from __future__ import annotations

from math import isfinite

from backend.models.zone import ZoneType
from backend.models.zone_boundary import BoundaryReasonCode, BoundarySet


class BoundaryValidationError(ValueError):
    """Boundary rejection carrying a stable machine-readable reason code."""

    def __init__(self, reason_code: BoundaryReasonCode, message: str) -> None:
        self.reason_code = reason_code
        super().__init__(message)


class ZoneBoundaryValidator:
    """Reject malformed, non-positive, inverted and zero-width boundaries."""

    @staticmethod
    def validate(zone_type: ZoneType, boundary: BoundarySet) -> None:
        values = (boundary.proximal, boundary.distal)
        valid_numbers = all(
            isinstance(value, (int, float)) and isfinite(value)
            for value in values
        )
        if not valid_numbers:
            raise BoundaryValidationError(
                BoundaryReasonCode.MALFORMED_BOUNDARY,
                "Boundary values must be finite numbers.",
            )
        if boundary.proximal <= 0 or boundary.distal <= 0:
            raise BoundaryValidationError(
                BoundaryReasonCode.NON_POSITIVE_BOUNDARY,
                "Boundary values must be greater than zero.",
            )
        if boundary.proximal == boundary.distal:
            raise BoundaryValidationError(
                BoundaryReasonCode.ZERO_WIDTH_BOUNDARY,
                "Proximal and distal cannot be equal.",
            )
        inverted = (
            boundary.proximal < boundary.distal
            if zone_type == ZoneType.DEMAND
            else boundary.proximal > boundary.distal
        )
        if inverted:
            raise BoundaryValidationError(
                BoundaryReasonCode.INVERTED_BOUNDARY,
                "Boundary orientation does not match the zone type.",
            )
