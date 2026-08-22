"""AlphaEdge Canonical Trade Planning V1.

This engine consumes immutable same-snapshot canonical zones. It owns no
formation, boundary, lifecycle, authenticity, quality, confidence or ranking
methodology and never creates an execution-ready protective stop.
"""

from __future__ import annotations

import math

from backend.models.canonical_trade_plan import (
    CanonicalPlanningZone,
    CanonicalTradePlan,
    CanonicalTradePlanStatus,
    ProtectiveStopStatus,
    TradePlanReasonCode,
)


class CanonicalTradePlanningEngine:
    """Build one direction-aware structural plan from canonical coordinates."""

    def build(
        self,
        selected: CanonicalPlanningZone,
        zones: tuple[CanonicalPlanningZone, ...],
        *,
        expected_snapshot_id: str,
        expected_methodology_version: str,
    ) -> CanonicalTradePlan:
        unavailable = self._selected_zone_failure(
            selected,
            zones,
            expected_snapshot_id,
            expected_methodology_version,
        )
        if unavailable is not None:
            return self._unavailable(selected, unavailable)

        demand = selected.zone_type == "DEMAND"
        lower = min(selected.proximal, selected.distal)
        upper = max(selected.proximal, selected.distal)
        entry = selected.proximal
        invalidation = selected.distal
        candidates = [
            zone
            for zone in zones
            if zone.zone_id != selected.zone_id
            and zone.symbol == selected.symbol
            and zone.timeframe == selected.timeframe
            and zone.snapshot_id == selected.snapshot_id
            and zone.methodology_version == selected.methodology_version
            and zone.zone_type != selected.zone_type
            and zone.formation_evidence_available
            and zone.authenticity_status == "AUTHENTIC"
            and zone.is_active
            and not zone.is_removed
            and zone.lifecycle_status not in {"INVALIDATED", "REMOVED"}
            and self._valid_boundaries(zone)
            and (zone.proximal > entry if demand else zone.proximal < entry)
        ]
        candidates.sort(key=lambda zone: zone.proximal, reverse=not demand)
        target_zone = candidates[0] if candidates else None
        distance_to_invalidation = (
            entry - invalidation if demand else invalidation - entry
        )
        common = {
            "selected_zone_id": selected.zone_id,
            "symbol": selected.symbol,
            "timeframe": selected.timeframe,
            "snapshot_id": selected.snapshot_id,
            "methodology_version": selected.methodology_version,
            "zone_type": selected.zone_type,
            "interaction_range": (round(lower, 2), round(upper, 2)),
            "planned_entry_reference": round(entry, 2),
            "structural_invalidation": round(invalidation, 2),
            "distance_entry_to_structural_invalidation": round(
                distance_to_invalidation, 2
            ),
            "protective_stop": None,
            "protective_stop_status": ProtectiveStopStatus.POLICY_NOT_DEFINED,
            "risk_per_share": None,
            "risk_reward": None,
        }
        stop_reason = TradePlanReasonCode.PROTECTIVE_STOP_REQUIRES_EXECUTION_POLICY
        if target_zone is None:
            return CanonicalTradePlan(
                **common,
                status=CanonicalTradePlanStatus.PARTIAL,
                target=None,
                target_zone_id=None,
                available_room=None,
                structural_reward_per_share=None,
                reason_codes=(TradePlanReasonCode.NO_VALID_OPPOSING_ZONE, stop_reason),
            )

        target = target_zone.proximal
        reward = target - entry if demand else entry - target
        if reward <= 0:
            return self._unavailable(
                selected,
                TradePlanReasonCode.NON_POSITIVE_STRUCTURAL_REWARD,
            )
        return CanonicalTradePlan(
            **common,
            status=CanonicalTradePlanStatus.COMPLETE_STRUCTURAL,
            target=round(target, 2),
            target_zone_id=target_zone.zone_id,
            available_room=round(reward, 2),
            structural_reward_per_share=round(reward, 2),
            reason_codes=(TradePlanReasonCode.PLAN_STRUCTURAL_COMPLETE, stop_reason),
        )

    def _selected_zone_failure(
        self,
        selected: CanonicalPlanningZone,
        zones: tuple[CanonicalPlanningZone, ...],
        snapshot_id: str,
        methodology_version: str,
    ) -> TradePlanReasonCode | None:
        if selected.snapshot_id != snapshot_id:
            return TradePlanReasonCode.SNAPSHOT_MISMATCH
        if selected.methodology_version != methodology_version:
            return TradePlanReasonCode.STALE_METHODOLOGY_VERSION
        matching = [zone for zone in zones if zone.zone_id == selected.zone_id]
        if not matching:
            return TradePlanReasonCode.SELECTED_ZONE_NOT_FOUND
        if matching[0] != selected:
            return TradePlanReasonCode.SELECTED_ZONE_OUT_OF_SYNC
        if selected.is_removed or selected.lifecycle_status == "REMOVED":
            return TradePlanReasonCode.ZONE_REMOVED
        if selected.lifecycle_status == "INVALIDATED" or not selected.is_active:
            return TradePlanReasonCode.ZONE_INVALIDATED
        if not selected.formation_evidence_available or not self._valid_boundaries(
            selected
        ):
            return TradePlanReasonCode.INVALID_CANONICAL_BOUNDARIES
        return None

    @staticmethod
    def _valid_boundaries(zone: CanonicalPlanningZone) -> bool:
        values = (zone.proximal, zone.distal)
        if not all(math.isfinite(value) and value > 0 for value in values):
            return False
        if zone.proximal == zone.distal:
            return False
        if zone.zone_type == "DEMAND":
            return zone.proximal > zone.distal
        if zone.zone_type == "SUPPLY":
            return zone.proximal < zone.distal
        return False

    @staticmethod
    def _unavailable(
        selected: CanonicalPlanningZone,
        reason: TradePlanReasonCode,
    ) -> CanonicalTradePlan:
        return CanonicalTradePlan(
            selected_zone_id=selected.zone_id,
            symbol=selected.symbol,
            timeframe=selected.timeframe,
            snapshot_id=selected.snapshot_id,
            methodology_version=selected.methodology_version,
            zone_type=selected.zone_type,
            status=CanonicalTradePlanStatus.UNAVAILABLE,
            interaction_range=None,
            planned_entry_reference=None,
            structural_invalidation=None,
            target=None,
            target_zone_id=None,
            available_room=None,
            structural_reward_per_share=None,
            distance_entry_to_structural_invalidation=None,
            protective_stop=None,
            protective_stop_status=ProtectiveStopStatus.POLICY_NOT_DEFINED,
            risk_per_share=None,
            risk_reward=None,
            reason_codes=(
                reason,
                TradePlanReasonCode.PROTECTIVE_STOP_REQUIRES_EXECUTION_POLICY,
            ),
        )
