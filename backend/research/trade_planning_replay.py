"""Look-ahead-safe research replay for Canonical Trade Planning V1.

This module is audit infrastructure only. Production scanner, ranking,
recommendations, and Stock Details do not import it.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from pandas import DataFrame

from backend.engines.demand_supply_engine.zone_authenticity_engine import (
    ZoneAuthenticityEngine,
)
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.engines.demand_supply_engine.zone_lifecycle_engine import (
    ZoneLifecycleEngine,
)
from backend.engines.trend_engine.canonical_trend_engine import CanonicalTrendEngine
from backend.models.trade_planning_replay import (
    ReplayEntryPolicy,
    ReplayObservation,
    ReplayOutcome,
    ReplayPlanSnapshot,
    ReplayStopPolicy,
)
from backend.models.zone import Zone, ZoneType
from backend.models.zone_authenticity import AuthenticityStatus
from backend.models.zone_lifecycle import ZoneLifecycleStatus
from backend.services.scanner.zone_lifecycle_ui_service import ZoneLifecycleUiService

ZONE_WIDTH_STOP_POLICIES = tuple(
    ReplayStopPolicy(f"ZONE_WIDTH_{percent}", zone_width_fraction=percent / 100)
    for percent in (5, 10, 15, 20, 25, 30)
)
ATR_STOP_POLICIES = tuple(
    ReplayStopPolicy(f"ATR14_{percent}", atr_fraction=percent / 100)
    for percent in (5, 10, 15, 20, 25, 30)
)
HYBRID_STOP_POLICIES = tuple(
    ReplayStopPolicy(
        f"HYBRID_MAX_ZW_ATR_{percent}",
        zone_width_fraction=percent / 100,
        atr_fraction=percent / 100,
        hybrid=True,
    )
    for percent in (5, 10, 15, 20, 25, 30)
)
DEFAULT_STOP_POLICIES = (
    ZONE_WIDTH_STOP_POLICIES + ATR_STOP_POLICIES + HYBRID_STOP_POLICIES
)

# Frozen research/backtesting horizons approved after the entry calibration.
# Horizon expiry is an observation boundary, never structural invalidation.
REPLAY_HORIZON_V1 = {"15m": 80, "75m": 48, "125m": 48, "1D": 80, "1W": 52}


@dataclass(frozen=True)
class ReplayResult:
    """Complete replay result and explicit data limitations."""

    snapshots: tuple[ReplayPlanSnapshot, ...]
    observations: tuple[ReplayObservation, ...]
    discovered_zone_count: int
    reconstructed_zone_count: int
    skipped_unreconstructed_count: int
    limitations: tuple[str, ...]


class TradePlanningReplayEngine:
    """Replay canonical zones without changing production methodology."""

    def __init__(self, detector: ZoneDetectionEngine | None = None) -> None:
        self._detector = detector or ZoneDetectionEngine()
        self._lifecycle = ZoneLifecycleEngine()
        self._authenticity = ZoneAuthenticityEngine()

    def replay(
        self,
        data: DataFrame,
        *,
        symbol: str,
        timeframe: str,
        entry_policies: tuple[ReplayEntryPolicy, ...] = tuple(ReplayEntryPolicy),
        stop_policies: tuple[ReplayStopPolicy, ...] = DEFAULT_STOP_POLICIES,
        tick_size: float | None = None,
        maximum_zones: int | None = None,
    ) -> ReplayResult:
        """Replay every reproducible canonical zone in ``data``.

        A full-history detection pass only discovers candidate planning indexes.
        Every studied zone is then re-detected from a prefix ending at that
        planning index. The prefix result is the sole source of plan facts.
        """

        self._validate_data(data)
        all_discovered = self._detector.detect_zones(data)
        discovered = self._sample_zones(all_discovered, maximum_zones)
        snapshots: list[ReplayPlanSnapshot] = []
        observations: list[ReplayObservation] = []
        skipped = 0

        for discovery in discovered:
            evidence = discovery.formation_evidence
            if evidence is None:
                skipped += 1
                continue
            planning_index = evidence.leg_out_end_index
            if planning_index >= len(data) - 1:
                continue
            prefix = data.iloc[: planning_index + 1].copy()
            known = self._detector.detect_zones(prefix)
            selected = self._match_zone(discovery, known)
            if selected is None:
                skipped += 1
                continue
            snapshot = self._snapshot(
                prefix,
                selected,
                known,
                all_discovered,
                symbol=symbol,
                timeframe=timeframe,
                planning_index=planning_index,
                tick_size=tick_size,
            )
            snapshots.append(snapshot)
            future = data.iloc[planning_index + 1 :]
            for entry_policy in entry_policies:
                for stop_policy in stop_policies:
                    observation = self._observe(
                        data,
                        future,
                        selected,
                        snapshot,
                        entry_policy,
                        stop_policy,
                    )
                    if observation is not None:
                        observations.append(observation)

        limitations = []
        if tick_size is None:
            limitations.append(
                "Instrument-specific tick-size metadata unavailable; no tick "
                "component was added to hybrid stop candidates."
            )
        return ReplayResult(
            snapshots=tuple(snapshots),
            observations=tuple(observations),
            discovered_zone_count=len(all_discovered),
            reconstructed_zone_count=len(snapshots),
            skipped_unreconstructed_count=skipped,
            limitations=tuple(limitations),
        )

    @staticmethod
    def _sample_zones(zones: list[Zone], maximum: int | None) -> list[Zone]:
        """Return deterministic, history-spanning audit samples only."""

        if maximum is None or len(zones) <= maximum:
            return zones
        if maximum <= 0:
            raise ValueError("maximum_zones must be positive when supplied.")
        if maximum == 1:
            return [zones[len(zones) // 2]]
        indexes = {
            round(position * (len(zones) - 1) / (maximum - 1))
            for position in range(maximum)
        }
        return [zones[index] for index in sorted(indexes)]

    def _snapshot(
        self,
        prefix: DataFrame,
        selected: Zone,
        known: list[Zone],
        all_discovered: list[Zone],
        *,
        symbol: str,
        timeframe: str,
        planning_index: int,
        tick_size: float | None,
    ) -> ReplayPlanSnapshot:
        current_price = float(prefix["Close"].iloc[-1])
        active_indexes: set[int] = set()
        definitions = {}
        candles = tuple(ZoneLifecycleUiService._candles(prefix))
        lifecycle_by_index = {}
        for zone in known:
            definition = ZoneLifecycleUiService._definition(
                zone, prefix, symbol, timeframe
            )
            definitions[zone.created_index] = definition
            lifecycle = self._lifecycle.evaluate(
                definition, candles, current_price=current_price
            )
            lifecycle_by_index[zone.created_index] = lifecycle
            if lifecycle.is_active and lifecycle.lifecycle_status not in {
                ZoneLifecycleStatus.INVALIDATED,
                ZoneLifecycleStatus.REMOVED,
            }:
                active_indexes.add(zone.created_index)

        # Exact-price computational precision is not an instrument tick-size
        # assumption. It prevents the current provider's missing tick metadata
        # from contaminating stop buffers while retaining canonical identity
        # comparison for this audit.
        identity_precision = tick_size if tick_size is not None else 1e-8
        authenticity = self._authenticity.classify(
            known,
            prefix,
            symbol=symbol,
            timeframe=timeframe,
            tick_size=identity_precision,
            active_zone_indexes=active_indexes,
        )
        authenticity_by_index = {item.zone.created_index: item for item in authenticity}
        opposing_at_planning = [
            zone for zone in known if zone.zone_type != selected.zone_type
        ]
        directionally_ahead = [
            zone
            for zone in opposing_at_planning
            if self._directionally_ahead(selected, zone)
        ]
        active_ahead = [
            zone for zone in directionally_ahead if zone.created_index in active_indexes
        ]
        eligible = []
        for zone in known:
            if zone.zone_type == selected.zone_type:
                continue
            lifecycle = lifecycle_by_index[zone.created_index]
            authentic = authenticity_by_index[zone.created_index]
            if (
                zone.created_index in active_indexes
                and authentic.status == AuthenticityStatus.AUTHENTIC
                and self._directionally_ahead(selected, zone)
            ):
                eligible.append(zone)
        opposing = self._nearest_opposing(selected, eligible)
        target = self._target_boundary(opposing) if opposing else None
        target_reason = "AVAILABLE"
        if opposing is None:
            future_opposing = [
                zone
                for zone in all_discovered
                if zone.created_index > planning_index
                and zone.zone_type != selected.zone_type
                and self._directionally_ahead(selected, zone)
            ]
            if not opposing_at_planning:
                target_reason = (
                    "OPPOSING_FORMED_LATER"
                    if future_opposing
                    else "NO_OPPOSING_ZONE_AT_PLANNING"
                )
            elif not directionally_ahead:
                target_reason = "DIRECTION_RESTRICTION"
            elif not active_ahead:
                target_reason = "LIFECYCLE_INELIGIBLE"
            else:
                target_reason = "AUTHENTICITY_INELIGIBLE"
        definition = definitions[selected.created_index]
        evidence = selected.formation_evidence
        assert evidence is not None
        atr_series = CanonicalTrendEngine.wilder_atr(prefix, period=14)
        atr_value = float(atr_series.iloc[-1]) if len(atr_series) else float("nan")
        atr14 = atr_value if isfinite(atr_value) and atr_value > 0 else None
        low, high = sorted((selected.lower_price, selected.upper_price))
        opposing_id = None
        if opposing is not None:
            opposing_id = authenticity_by_index[opposing.created_index].zone_id
        return ReplayPlanSnapshot(
            zone_id=authenticity_by_index[selected.created_index].zone_id,
            symbol=symbol,
            timeframe=timeframe,
            pattern=evidence.pattern,
            zone_type=selected.zone_type.value,
            planning_index=planning_index,
            planning_timestamp=str(prefix.index[-1]),
            interaction_low=low,
            interaction_high=high,
            structural_invalidation=definition.distal,
            opposing_zone_id=opposing_id,
            structural_target=target,
            atr14=atr14,
            prefix_candle_count=len(prefix),
            known_zone_count=len(known),
            target_eligible_zone_count=len(eligible),
            target_availability_reason=target_reason,
            selected_lifecycle_status=(
                lifecycle_by_index[selected.created_index].lifecycle_status.value
            ),
            selected_authenticity_status=(
                authenticity_by_index[selected.created_index].status.value
            ),
            tick_size=tick_size,
        )

    @staticmethod
    def _observe(
        data: DataFrame,
        future: DataFrame,
        zone: Zone,
        snapshot: ReplayPlanSnapshot,
        entry_policy: ReplayEntryPolicy,
        stop_policy: ReplayStopPolicy,
    ) -> ReplayObservation | None:
        demand = zone.zone_type == ZoneType.DEMAND
        entry = TradePlanningReplayEngine._entry_price(snapshot, demand, entry_policy)
        width = snapshot.interaction_high - snapshot.interaction_low
        buffer = TradePlanningReplayEngine._stop_buffer(
            width, snapshot.atr14, snapshot.tick_size, stop_policy
        )
        if not isfinite(buffer):
            return None
        stop = (
            snapshot.structural_invalidation - buffer
            if demand
            else snapshot.structural_invalidation + buffer
        )
        target = snapshot.structural_target
        risk = entry - stop if demand else stop - entry
        reward = (
            None if target is None else (target - entry if demand else entry - target)
        )
        rr = reward / risk if reward is not None and reward > 0 and risk > 0 else None

        entry_position = None
        for position, (_, candle) in enumerate(future.iterrows()):
            if float(candle["Low"]) <= entry <= float(candle["High"]):
                entry_position = position
                break
        if entry_position is None:
            return TradePlanningReplayEngine._empty_observation(
                snapshot,
                entry_policy,
                stop_policy,
                entry,
                stop,
                target,
                risk,
                reward,
                rr,
                ReplayOutcome.ENTRY_NOT_REACHED,
            )

        entered = future.iloc[entry_position:]
        horizon = REPLAY_HORIZON_V1.get(snapshot.timeframe)
        if horizon is not None:
            entered = entered.iloc[:horizon]
        entry_label = entered.index[0]
        mae = 0.0
        mfe = 0.0
        outcome = ReplayOutcome.OPEN_AT_END
        outcome_index = None
        outcome_timestamp = None
        first_stop_index = None
        first_stop_timestamp = None
        first_target_index = None
        first_target_timestamp = None
        first_failure_index = None
        first_failure_timestamp = None
        mae_before_target = 0.0
        distal_breached = False
        for local_position, (timestamp, candle) in enumerate(entered.iterrows()):
            low = float(candle["Low"])
            high = float(candle["High"])
            if demand:
                mae = max(mae, entry - low)
                mfe = max(mfe, high - entry)
                stop_hit = low <= stop
                target_hit = target is not None and high >= target
                distal_breached = (
                    distal_breached or low < snapshot.structural_invalidation
                )
                structural_failure = low < snapshot.structural_invalidation
            else:
                mae = max(mae, high - entry)
                mfe = max(mfe, entry - low)
                stop_hit = high >= stop
                target_hit = target is not None and low <= target
                distal_breached = (
                    distal_breached or high > snapshot.structural_invalidation
                )
                structural_failure = high > snapshot.structural_invalidation
            absolute_index = (
                snapshot.planning_index + 1 + entry_position + local_position
            )
            if stop_hit and first_stop_index is None:
                first_stop_index = absolute_index
                first_stop_timestamp = str(timestamp)
            if target_hit and first_target_index is None:
                first_target_index = absolute_index
                first_target_timestamp = str(timestamp)
                mae_before_target = mae
            if structural_failure and first_failure_index is None:
                first_failure_index = absolute_index
                first_failure_timestamp = str(timestamp)
            if outcome_index is None:
                if stop_hit and target_hit:
                    outcome = ReplayOutcome.AMBIGUOUS_SAME_CANDLE
                elif target_hit:
                    outcome = ReplayOutcome.TARGET_BEFORE_STOP
                elif stop_hit:
                    outcome = ReplayOutcome.STOP_BEFORE_TARGET
                else:
                    continue
                outcome_index = absolute_index
                outcome_timestamp = str(timestamp)
        if target is None:
            outcome = ReplayOutcome.NO_VALID_OPPOSING_ZONE
        return ReplayObservation(
            zone_id=snapshot.zone_id,
            symbol=snapshot.symbol,
            timeframe=snapshot.timeframe,
            pattern=snapshot.pattern,
            zone_type=snapshot.zone_type,
            entry_policy=entry_policy,
            stop_policy=stop_policy.name,
            entry_price=entry,
            stop_price=stop,
            target_price=target,
            risk_per_share=risk,
            reward_per_share=reward,
            structural_risk_reward=rr,
            entry_index=snapshot.planning_index + 1 + entry_position,
            entry_timestamp=str(entry_label),
            candles_to_entry=entry_position + 1,
            outcome=outcome,
            outcome_index=outcome_index,
            outcome_timestamp=outcome_timestamp,
            first_stop_index=first_stop_index,
            first_stop_timestamp=first_stop_timestamp,
            first_target_index=first_target_index,
            first_target_timestamp=first_target_timestamp,
            first_structural_failure_index=first_failure_index,
            first_structural_failure_timestamp=first_failure_timestamp,
            future_candle_count=len(entered),
            mae_price=mae,
            mfe_price=mfe,
            mae_zone_width=mae / width if width > 0 else None,
            mfe_zone_width=mfe / width if width > 0 else None,
            mae_atr=mae / snapshot.atr14 if snapshot.atr14 else None,
            mfe_atr=mfe / snapshot.atr14 if snapshot.atr14 else None,
            mae_before_target_price=(
                mae_before_target if first_target_index is not None else None
            ),
            mae_before_target_zone_width=(
                mae_before_target / width
                if first_target_index is not None and width > 0
                else None
            ),
            mae_before_target_atr=(
                mae_before_target / snapshot.atr14
                if first_target_index is not None and snapshot.atr14
                else None
            ),
            distal_breached_before_target=distal_breached,
        )

    @staticmethod
    def _entry_price(
        snapshot: ReplayPlanSnapshot,
        demand: bool,
        policy: ReplayEntryPolicy,
    ) -> float:
        if policy == ReplayEntryPolicy.MIDPOINT:
            return (snapshot.interaction_low + snapshot.interaction_high) / 2
        if policy == ReplayEntryPolicy.PROXIMAL:
            return snapshot.interaction_high if demand else snapshot.interaction_low
        return snapshot.interaction_low if demand else snapshot.interaction_high

    @staticmethod
    def _stop_buffer(
        width: float,
        atr14: float | None,
        tick_size: float | None,
        policy: ReplayStopPolicy,
    ) -> float:
        components = [width * policy.zone_width_fraction]
        if policy.atr_fraction:
            if atr14 is None:
                return float("nan")
            components.append(atr14 * policy.atr_fraction)
        if policy.hybrid and tick_size is not None:
            components.append(tick_size)
        return max(components) if policy.hybrid else sum(components)

    @staticmethod
    def _match_zone(discovery: Zone, known: list[Zone]) -> Zone | None:
        for zone in known:
            if (
                zone.zone_type == discovery.zone_type
                and zone.created_index == discovery.created_index
                and zone.pattern_type == discovery.pattern_type
                and abs(zone.lower_price - discovery.lower_price) < 1e-9
                and abs(zone.upper_price - discovery.upper_price) < 1e-9
            ):
                return zone
        return None

    @staticmethod
    def _directionally_ahead(selected: Zone, opposing: Zone) -> bool:
        if selected.zone_type == ZoneType.DEMAND:
            return opposing.lower_price > selected.upper_price
        return opposing.upper_price < selected.lower_price

    @staticmethod
    def _nearest_opposing(selected: Zone, zones: list[Zone]) -> Zone | None:
        if not zones:
            return None
        if selected.zone_type == ZoneType.DEMAND:
            return min(zones, key=lambda item: item.lower_price)
        return max(zones, key=lambda item: item.upper_price)

    @staticmethod
    def _target_boundary(zone: Zone) -> float:
        return (
            zone.lower_price if zone.zone_type == ZoneType.SUPPLY else zone.upper_price
        )

    @staticmethod
    def _validate_data(data: DataFrame) -> None:
        required = {"Open", "High", "Low", "Close"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError(f"Missing OHLC columns: {sorted(missing)}")
        if data.empty or not data.index.is_monotonic_increasing:
            raise ValueError("Replay data must be non-empty and date-sorted.")

    @staticmethod
    def _empty_observation(
        snapshot: ReplayPlanSnapshot,
        entry_policy: ReplayEntryPolicy,
        stop_policy: ReplayStopPolicy,
        entry: float,
        stop: float,
        target: float | None,
        risk: float,
        reward: float | None,
        rr: float | None,
        outcome: ReplayOutcome,
    ) -> ReplayObservation:
        return ReplayObservation(
            zone_id=snapshot.zone_id,
            symbol=snapshot.symbol,
            timeframe=snapshot.timeframe,
            pattern=snapshot.pattern,
            zone_type=snapshot.zone_type,
            entry_policy=entry_policy,
            stop_policy=stop_policy.name,
            entry_price=entry,
            stop_price=stop,
            target_price=target,
            risk_per_share=risk,
            reward_per_share=reward,
            structural_risk_reward=rr,
            entry_index=None,
            entry_timestamp=None,
            candles_to_entry=None,
            outcome=outcome,
            outcome_index=None,
            outcome_timestamp=None,
            first_stop_index=None,
            first_stop_timestamp=None,
            first_target_index=None,
            first_target_timestamp=None,
            first_structural_failure_index=None,
            first_structural_failure_timestamp=None,
            future_candle_count=0,
            mae_price=None,
            mfe_price=None,
            mae_zone_width=None,
            mfe_zone_width=None,
            mae_atr=None,
            mfe_atr=None,
            mae_before_target_price=None,
            mae_before_target_zone_width=None,
            mae_before_target_atr=None,
            distal_breached_before_target=False,
        )
