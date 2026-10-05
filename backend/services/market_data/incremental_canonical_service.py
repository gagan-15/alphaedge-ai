"""Dependency-aware canonical formation refresh for completed EOD candles.

The trusted :class:`ZoneDetectionEngine` remains the only formation engine.
This adapter narrows candidate Base evaluation to the mathematically affected
suffix and reuses immutable earlier formation records.  It owns no analytical
thresholds or rules.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import pandas as pd
from pandas import DataFrame

from backend.engines.demand_supply_engine.candle_classifier import CandleClassifier
from backend.engines.demand_supply_engine.zone_detection_engine import ZoneDetectionEngine
from backend.models.candle_classification import CandleDirection, CandleStructure
from backend.models.zone import Zone
from backend.services.market_data.dhan_zone_rehydration import rehydrate_zone
from backend.validators.market_data_validator import MarketDataValidator


@dataclass(frozen=True)
class IncrementalCanonicalResult:
    zones: list[Zone]
    minimum_recomputed_base_end: int
    reused_zones: int
    recomputed_zones: int


class IncrementalCanonicalService:
    """Reuse immutable formations and detect only dependency-affected Bases."""

    # Existing frozen dependencies, expressed as execution context only:
    # CandleClassifier range median=20, departure ATR=14,
    # LegIn structural range=20/max walk=12, conditional Base maximum=5.
    CLASSIFICATION_LOOKBACK = 20
    DEPARTURE_ATR_LOOKBACK = 14
    STRUCTURAL_LOOKBACK = 20
    STRUCTURAL_WALK = 12
    CONDITIONAL_BASE_MAXIMUM = 5

    def __init__(self) -> None:
        self._classifier = CandleClassifier()
        self._detector = ZoneDetectionEngine()

    def affected_base_end_start(
        self, data: DataFrame, earliest_changed_index: int,
        *, append_only: bool = False,
    ) -> int:
        """Return a conservative exact-context boundary for candidate Bases.

        A correction can alter classifier rolling ranges for the following 20
        candles, ATR for 14, and structural evidence for another bounded walk.
        Maximal aligned exciting legs are not assumed to be bounded: the
        boundary is extended backwards across the actual contiguous run.
        """
        if data.empty:
            return 0
        self._classifier.clear_cache()
        changed = max(0, min(int(earliest_changed_index), len(data) - 1))
        bounded = (
            self.CONDITIONAL_BASE_MAXIMUM
            if append_only else (
                self.CLASSIFICATION_LOOKBACK
                + self.DEPARTURE_ATR_LOOKBACK
                + self.STRUCTURAL_LOOKBACK
                + self.STRUCTURAL_WALK
                + self.CONDITIONAL_BASE_MAXIMUM
            )
        )
        cursor = max(0, changed - bounded)
        if cursor == 0:
            return 0

        # A maximal Leg-In can be arbitrarily long under the frozen engine.
        # Walk across the real contiguous aligned exciting run rather than
        # imposing a new analytical maximum.
        current = self._classifier.classify(data, cursor)
        direction = current.direction
        if (
            current.structure == CandleStructure.EXCITING
            and direction in {CandleDirection.BULLISH, CandleDirection.BEARISH}
        ):
            while cursor > 0:
                previous = self._classifier.classify(data, cursor - 1)
                if (
                    previous.structure != CandleStructure.EXCITING
                    or previous.direction != direction
                ):
                    break
                left = data.iloc[cursor - 1]
                right = data.iloc[cursor]
                if (
                    float(right["Low"]) > float(left["High"])
                    or float(right["High"]) < float(left["Low"])
                ):
                    break
                cursor -= 1
        return max(0, cursor - self.CONDITIONAL_BASE_MAXIMUM)

    def refresh(
        self,
        data: DataFrame,
        prior_payloads: list[object],
        earliest_changed_index: int,
        *, append_only: bool = False,
    ) -> IncrementalCanonicalResult:
        """Return the same canonical set while avoiding immutable history."""
        cutoff = self.affected_base_end_start(
            data, earliest_changed_index, append_only=append_only,
        )
        prior = [
            rehydrate_zone(
                json.loads(str(value["payload"]))
                if hasattr(value, "keys") and "payload" in value.keys()
                else value
            )
            for value in prior_payloads
        ]
        reused = [zone for zone in prior if zone.created_index < cutoff]
        recomputed = self._detector.detect_zones_from_base_end(data, cutoff)
        # The two sets are disjoint by immutable Base end index.
        zones = sorted(
            [*reused, *recomputed],
            key=lambda zone: (
                zone.created_index,
                zone.zone_type.value,
                zone.lower_price,
                zone.upper_price,
                zone.pattern_type or "",
            ),
        )
        return IncrementalCanonicalResult(
            zones=zones,
            minimum_recomputed_base_end=cutoff,
            reused_zones=len(reused),
            recomputed_zones=len(recomputed),
        )

    @staticmethod
    def _stamp_key(value: object) -> int:
        stamp = pd.Timestamp(value)
        if stamp.tzinfo is not None:
            stamp = stamp.tz_convert("UTC").tz_localize(None)
        return int(stamp.value)

    def refresh_validated(
        self, data: DataFrame, prior_payloads: list[object],
        earliest_changed_timestamp: object, *, append_only: bool | None = None,
    ) -> IncrementalCanonicalResult:
        """Refresh the affected validated segment and preserve other segments."""
        raw_payloads = [
            json.loads(str(value["payload"]))
            if hasattr(value, "keys") and "payload" in value.keys() else value
            for value in prior_payloads
        ]
        changed_key = self._stamp_key(earliest_changed_timestamp)
        remaining = list(raw_payloads)
        combined: list[Zone] = []
        reused = recomputed = 0
        minimum = 0
        for segment in MarketDataValidator.validate_segments(data).segments:
            keys = {self._stamp_key(value) for value in segment.index}
            segment_payloads = []
            for payload in list(remaining):
                evidence = payload.get("formation_evidence")
                if not evidence or not evidence.get("base_timestamps"):
                    raise ValueError("Structured Base timestamp is required.")
                if self._stamp_key(evidence["base_timestamps"][0]) in keys:
                    segment_payloads.append(payload)
                    remaining.remove(payload)
            affected = changed_key in keys
            if not affected:
                zones = [rehydrate_zone(payload) for payload in segment_payloads]
                combined.extend(zones)
                reused += len(zones)
                continue
            local_index = next(
                index for index, value in enumerate(segment.index)
                if self._stamp_key(value) == changed_key
            )
            tail_only = (
                local_index >= len(segment) - 2
                if append_only is None else append_only
            )
            result = self.refresh(
                segment, segment_payloads, local_index, append_only=tail_only,
            )
            combined.extend(result.zones)
            reused += result.reused_zones
            recomputed += result.recomputed_zones
            minimum = result.minimum_recomputed_base_end
        if remaining:
            raise ValueError("Prior canonical zones do not map to validated data segments.")
        return IncrementalCanonicalResult(combined, minimum, reused, recomputed)
