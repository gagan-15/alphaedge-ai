"""Primary Dashboard policy over canonical zone lifecycle facts."""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.zone_lifecycle import (
    ZoneLifecycleResult,
    ZoneLifecycleStatus,
)


@dataclass(frozen=True)
class DashboardLifecycleEligibility:
    """Explain whether a canonical lifecycle may appear on the Dashboard."""

    eligible: bool
    reason_code: str


class DashboardLifecycleEligibilityService:
    """Apply Policy B without changing any canonical lifecycle state."""

    def evaluate(
        self,
        lifecycle: ZoneLifecycleResult,
    ) -> DashboardLifecycleEligibility:
        if (
            lifecycle.is_removed
            or lifecycle.lifecycle_status
            in (ZoneLifecycleStatus.INVALIDATED, ZoneLifecycleStatus.REMOVED)
        ):
            return DashboardLifecycleEligibility(
                eligible=False,
                reason_code="LIFECYCLE_INVALIDATED",
            )
        if lifecycle.is_reacting:
            return DashboardLifecycleEligibility(
                eligible=True,
                reason_code="LIFECYCLE_REACTING",
            )
        if lifecycle.is_fresh and lifecycle.test_count == 0:
            return DashboardLifecycleEligibility(
                eligible=True,
                reason_code="LIFECYCLE_FRESH",
            )
        if lifecycle.test_count >= 2:
            return DashboardLifecycleEligibility(
                eligible=False,
                reason_code="LIFECYCLE_RETESTED",
            )
        return DashboardLifecycleEligibility(
            eligible=False,
            reason_code="LIFECYCLE_TESTED",
        )
