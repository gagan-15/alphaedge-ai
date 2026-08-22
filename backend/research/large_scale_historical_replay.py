"""Uncapped, point-in-time Daily/Weekly replay for Milestone 9C.

Research only. Production scanner, ranking, and UI do not import this module.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from pandas import DataFrame

from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.models.trade_planning_replay import (
    ReplayEntryPolicy,
    ReplayStopPolicy,
)
from backend.models.zone import Zone
from backend.research.historical_context_validation import (
    HistoricalContextReconstructor,
)
from backend.research.trade_planning_replay import TradePlanningReplayEngine


RESEARCH_STOP = ReplayStopPolicy(
    "RESEARCH_ONLY_NOT_CANONICAL_STOP", zone_width_fraction=0.01
)


class LargeScaleHistoricalReplayEngine:
    """Enumerate every canonical zone without repeated formation detection."""

    def __init__(self) -> None:
        self._detector = ZoneDetectionEngine()
        self._planning = TradePlanningReplayEngine(self._detector)
        self._context = HistoricalContextReconstructor()

    def replay(
        self,
        execution: DataFrame,
        *,
        symbol: str,
        timeframe: str,
        location: DataFrame,
        trend: DataFrame,
    ) -> dict[str, Any]:
        """Return immutable snapshots, outcomes, and context for all zones."""

        zones = self._detector.detect_zones(execution)
        location_zones = self._detector.detect_zones(location)
        snapshots = []
        observations = []
        contexts = []
        skipped = 0
        for selected in zones:
            evidence = selected.formation_evidence
            if evidence is None or evidence.leg_out_end_index >= len(execution) - 1:
                skipped += 1
                continue
            planning_index = evidence.leg_out_end_index
            prefix = execution.iloc[: planning_index + 1].copy()
            known = self._known_at(zones, planning_index)
            snapshot = self._planning._snapshot(
                prefix,
                selected,
                known,
                zones,
                symbol=symbol,
                timeframe=timeframe,
                planning_index=planning_index,
                tick_size=None,
            )
            future = execution.iloc[planning_index + 1 :]
            observation = self._planning._observe(
                execution,
                future,
                selected,
                snapshot,
                ReplayEntryPolicy.PROXIMAL,
                RESEARCH_STOP,
            )
            snapshot_row = asdict(snapshot)
            snapshots.append(snapshot_row)
            if observation is not None:
                row = asdict(observation)
                row["entry_policy"] = row["entry_policy"].value
                row["outcome"] = row["outcome"].value
                observations.append(row)
            contexts.append(
                self._context.reconstruct(
                    snapshot_row,
                    execution,
                    location_data=location,
                    trend_data=trend,
                    execution_zones=zones,
                    location_zones=location_zones,
                )
            )
        return {
            "snapshots": snapshots,
            "observations": observations,
            "contexts": contexts,
            "discovered": len(zones),
            "reconstructed": len(snapshots),
            "skipped": skipped,
        }

    @staticmethod
    def _known_at(zones: list[Zone], planning_index: int) -> list[Zone]:
        return [
            zone
            for zone in zones
            if zone.formation_evidence is not None
            and zone.formation_evidence.leg_out_end_index <= planning_index
        ]
