from __future__ import annotations

from backend.models.zone_lifecycle import (
    ZoneLifecycleResult,
    ZoneLifecycleStatus,
)
from backend.services.scanner.dashboard_lifecycle_eligibility_service import (
    DashboardLifecycleEligibilityService,
)


def _result(
    status: ZoneLifecycleStatus,
    *,
    fresh: bool = False,
    reacting: bool = False,
    tests: int = 0,
    removed: bool = False,
) -> ZoneLifecycleResult:
    return ZoneLifecycleResult(
        zone_id="TEST:1D:1",
        symbol="TEST",
        source_timeframe="1D",
        lifecycle_status=status,
        structural_status=status,
        is_fresh=fresh,
        is_approaching=False,
        test_count=tests,
        visit_count=tests,
        penetration_percent=0,
        max_penetration_percent=0,
        current_interaction=None,
        last_interaction=None,
        last_tested_at=None,
        invalidated_at=None,
        invalidation_reason=None,
        is_reacting=reacting,
        is_removed=removed,
        is_active=not removed,
    )


def test_fresh_zone_is_primary_dashboard_eligible() -> None:
    observed = DashboardLifecycleEligibilityService().evaluate(
        _result(ZoneLifecycleStatus.FRESH, fresh=True)
    )
    assert observed.eligible
    assert observed.reason_code == "LIFECYCLE_FRESH"


def test_current_reaction_is_primary_dashboard_eligible() -> None:
    observed = DashboardLifecycleEligibilityService().evaluate(
        _result(ZoneLifecycleStatus.REACTING, reacting=True, tests=1)
    )
    assert observed.eligible
    assert observed.reason_code == "LIFECYCLE_REACTING"


def test_tested_once_is_excluded_even_when_formation_is_strong() -> None:
    formation_qualified = True
    observed = DashboardLifecycleEligibilityService().evaluate(
        _result(ZoneLifecycleStatus.TESTED_RESPECTED, tests=1)
    )
    assert formation_qualified and not observed.eligible
    assert observed.reason_code == "LIFECYCLE_TESTED"


def test_retested_zone_is_excluded() -> None:
    observed = DashboardLifecycleEligibilityService().evaluate(
        _result(ZoneLifecycleStatus.RETESTED, tests=2)
    )
    assert not observed.eligible
    assert observed.reason_code == "LIFECYCLE_RETESTED"


def test_invalidated_or_removed_zone_is_excluded() -> None:
    service = DashboardLifecycleEligibilityService()
    invalidated = service.evaluate(_result(ZoneLifecycleStatus.INVALIDATED, tests=1))
    removed = service.evaluate(
        _result(ZoneLifecycleStatus.REMOVED, tests=1, removed=True)
    )
    assert not invalidated.eligible
    assert invalidated.reason_code == "LIFECYCLE_INVALIDATED"
    assert not removed.eligible
    assert removed.reason_code == "LIFECYCLE_INVALIDATED"


def test_canonical_tested_state_wins_over_legacy_fresh_flag() -> None:
    legacy_zone_is_fresh = True
    canonical = _result(ZoneLifecycleStatus.TESTED_RESPECTED, tests=1)
    observed = DashboardLifecycleEligibilityService().evaluate(canonical)
    assert legacy_zone_is_fresh
    assert not observed.eligible
    assert observed.reason_code == "LIFECYCLE_TESTED"
