# flake8: noqa: E501
"""Point-in-time Zone Quality and Trade Confidence reconstruction.

Research-only adapter.  It composes frozen production engines from candle
prefixes and is intentionally not imported by scanner or UI code.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd
from pandas import DataFrame

from backend.config.gtf_workflow_roles import resolve_gtf_workflow
from backend.engines.demand_supply_engine.zone_detection_engine import ZoneDetectionEngine
from backend.engines.trade_confidence_engine import CanonicalTradeConfidenceEngine
from backend.engines.trend_engine.canonical_trend_engine import CanonicalTrendEngine
from backend.engines.zone_scoring_engine.zone_scoring_engine import ZoneScoringEngine
from backend.models.canonical_zone_analysis import CanonicalZoneAnalysis
from backend.models.zone import Zone
from backend.models.zone_scoring.canonical_zone_quality import ZoneQualityContext
from backend.services.scanner.timeframe_confluence_service import TimeframeConfluenceService
from backend.services.scanner.zone_lifecycle_ui_service import ZoneLifecycleUiService


class HistoricalContextReconstructor:
    """Rebuild immutable canonical context using data known at one timestamp."""

    def __init__(self) -> None:
        self._detector = ZoneDetectionEngine()
        self._quality = ZoneScoringEngine()
        self._trend = CanonicalTrendEngine()
        self._lifecycle = ZoneLifecycleUiService()
        self._location_cache: dict[tuple, tuple[list[Zone], dict, float]] = {}
        self._trend_cache: dict[tuple, Any] = {}

    @staticmethod
    def prefix(data: DataFrame | None, timestamp: object) -> DataFrame:
        if data is None or data.empty:
            return DataFrame()
        cutoff = pd.Timestamp(timestamp)
        index = pd.DatetimeIndex(data.index)
        if index.tz is not None and cutoff.tzinfo is None:
            cutoff = cutoff.tz_localize(index.tz)
        elif index.tz is None and cutoff.tzinfo is not None:
            cutoff = cutoff.tz_localize(None)
        return data.loc[index <= cutoff].copy()

    def reconstruct(
        self,
        snapshot: dict[str, Any],
        execution_data: DataFrame,
        *,
        location_data: DataFrame | None,
        trend_data: DataFrame | None,
        execution_zones: list[Zone] | None = None,
        location_zones: list[Zone] | None = None,
    ) -> dict[str, Any]:
        timestamp = snapshot["planning_timestamp"]
        execution = self.prefix(execution_data, timestamp)
        symbol = snapshot["symbol"]
        timeframe = snapshot["timeframe"]
        if execution_zones is None:
            zones = self._detector.detect_zones(execution)
        else:
            last_index = len(execution) - 1
            zones = [
                zone for zone in execution_zones
                if zone.formation_evidence is not None
                and zone.formation_evidence.leg_out_end_index <= last_index
            ]
        selected = self._match(snapshot, zones)
        if selected is None:
            return self._unavailable(snapshot, "HISTORICAL_ZONE_NOT_RECONSTRUCTED")

        metadata = self._lifecycle.evaluate(
            zones,
            execution,
            symbol=symbol,
            timeframe=timeframe,
            current_price=float(execution["Close"].iloc[-1]),
        )
        selected_meta = metadata[selected.created_index]
        quality_context = ZoneQualityContext(
            lifecycle_status=selected_meta.lifecycle_status,
            is_fresh=selected_meta.is_fresh,
            penetration_percent=selected_meta.current_penetration_percent,
            max_penetration_percent=selected_meta.max_penetration_percent,
            authenticity_status=selected_meta.authenticity_status,
        )
        quality = self._quality.score(
            [selected], {selected.created_index: quality_context}
        ).scored_zones[0]

        workflow = resolve_gtf_workflow(timeframe)
        location = self._location(
            selected,
            self.prefix(location_data, timestamp),
            symbol=symbol,
            timeframe=workflow.location,
            precomputed_zones=location_zones,
        )
        trend = self._trend_result(
            self.prefix(trend_data, timestamp),
            symbol=symbol,
            timeframe=workflow.trend,
            timestamp=timestamp,
        )
        alignment = self._trend.alignment(selected.zone_type.value, trend.trend_state)
        analysis = CanonicalZoneAnalysis(
            zone_id=selected_meta.zone_id,
            symbol=symbol,
            timeframe=timeframe,
            zone_type=selected.zone_type.value,
            pattern=selected.pattern_type or "UNKNOWN",
            proximal=(selected.upper_price if selected.zone_type.value == "DEMAND" else selected.lower_price),
            distal=(selected.lower_price if selected.zone_type.value == "DEMAND" else selected.upper_price),
            formation_evidence=selected.formation_evidence,
            lifecycle=selected_meta,
            authenticity=selected_meta.authenticity_status,
            zone_quality=quality,
            canonical_trend=trend,
            htf_context=location,
            alignment=alignment.value,
            significant_gap=bool(
                selected.formation_evidence
                and selected.formation_evidence.significant_gap
            ),
            gap_measurement=(
                selected.formation_evidence.gap_measurement
                if selected.formation_evidence
                else None
            ),
            trend_timeframe=workflow.trend,
            location_timeframe=workflow.location,
            trend_alignment=alignment.value,
            location_relationship=location["relationship"],
            location_compatibility=location["compatibility"],
            combined_context=None,
            data_sufficient=bool(trend.data_sufficient and location["available"]),
            reason_codes=tuple(location["reason_codes"])
            + tuple(item.value for item in trend.reason_codes),
        )
        confidence = CanonicalTradeConfidenceEngine.evaluate(analysis)
        return {
            "zone_id": snapshot["zone_id"],
            "symbol": symbol,
            "timeframe": timeframe,
            "planning_timestamp": timestamp,
            "zone_quality": {
                "status": "AVAILABLE",
                "score": quality.total_score,
                "label": quality.label,
                "components": [asdict(item) for item in quality.components],
                "unavailable_components": [],
            },
            "htf": location,
            "trend": trend.as_dict(),
            "trade_confidence": {
                "status": "AVAILABLE",
                "score": confidence.total_score,
                "label": confidence.label.value,
                "zone_quality_contribution": confidence.zone_quality_contribution,
                "htf_contribution": confidence.location_contribution,
                "trend_contribution": confidence.trend_contribution,
                "htf_relationship": confidence.htf_overlap_type,
                "htf_compatibility": confidence.htf_direction_compatibility,
                "trend_alignment": confidence.trend_alignment,
                "data_sufficiency": confidence.data_sufficiency.value,
                "conflicted": confidence.label.value == "CONFLICTED",
            },
        }

    def _location(
        self,
        execution: Zone,
        data: DataFrame,
        *,
        symbol: str,
        timeframe: str | None,
        precomputed_zones: list[Zone] | None = None,
    ) -> dict[str, Any]:
        if timeframe is None or data.empty:
            return {
                "available": False,
                "timeframe": timeframe,
                "relationship": "NO_OVERLAP",
                "compatibility": "NO_HTF_CONTEXT",
                "reason_codes": ["HTF_DATA_UNAVAILABLE"],
                "zone_id": None,
            }
        key = (symbol, timeframe, str(data.index[-1]), len(data))
        cached = self._location_cache.get(key)
        if cached is None:
            if precomputed_zones is None:
                zones = self._detector.detect_zones(data)
            else:
                last_index = len(data) - 1
                zones = [
                    zone
                    for zone in precomputed_zones
                    if zone.formation_evidence is not None
                    and zone.formation_evidence.leg_out_end_index <= last_index
                ]
            metadata = self._lifecycle.evaluate(
                zones,
                data,
                symbol=symbol,
                timeframe=timeframe,
                current_price=float(data["Close"].iloc[-1]),
            )
            eligible = [
                zone for zone in zones
                if metadata[zone.created_index].dashboard_lifecycle_eligible
            ]
            current = float(data["Close"].iloc[-1])
            self._location_cache[key] = (eligible, metadata, current)
        else:
            eligible, metadata, current = cached
        if not eligible:
            return {
                "available": True,
                "timeframe": timeframe,
                "relationship": "NO_OVERLAP",
                "compatibility": "NO_HTF_CONTEXT",
                "reason_codes": ["HTF_NO_ACTIVE_ZONE"],
                "zone_id": None,
            }
        low, high = sorted((execution.lower_price, execution.upper_price))
        candidates = []
        for zone in eligible:
            overlap = TimeframeConfluenceService.overlap_percent(
                low, high, zone.lower_price, zone.upper_price
            )
            distance = TimeframeConfluenceService.distance_percent(
                low, high, zone.lower_price, zone.upper_price, current
            )
            candidates.append((zone, overlap, distance))
        selected, overlap, distance = max(
            candidates,
            key=lambda item: (item[1], -item[2], item[0].created_index, item[0].zone_type.value),
        )
        relationship = TimeframeConfluenceService.overlap_relationship(
            low, high, selected.lower_price, selected.upper_price
        )
        compatibility = TimeframeConfluenceService.compatibility(
            execution.zone_type.value, selected.zone_type.value
        )
        return {
            "available": True,
            "timeframe": timeframe,
            "relationship": relationship,
            "compatibility": compatibility,
            "reason_codes": [TimeframeConfluenceService.reason_code(relationship, compatibility)],
            "zone_id": metadata[selected.created_index].zone_id,
            "overlap_percent": overlap,
            "distance_percent": distance,
        }

    def _trend_result(
        self,
        data: DataFrame,
        *,
        symbol: str,
        timeframe: str | None,
        timestamp: object,
    ):
        evaluated = pd.Timestamp(timestamp).to_pydatetime()
        key = (symbol, timeframe, str(data.index[-1]) if not data.empty else None, len(data))
        if key not in self._trend_cache:
            self._trend_cache[key] = self._trend.evaluate(
                symbol, timeframe, data, evaluated_at=evaluated
            )
        return self._trend_cache[key]

    @staticmethod
    def _match(snapshot: dict[str, Any], zones: list[Zone]) -> Zone | None:
        low = float(snapshot["interaction_low"])
        high = float(snapshot["interaction_high"])
        aliases = {
            "DROP_BASE_RALLY": "DBR",
            "RALLY_BASE_RALLY": "RBR",
            "RALLY_BASE_DROP": "RBD",
            "DROP_BASE_DROP": "DBD",
        }
        candidates = [
            zone for zone in zones
            if zone.zone_type.value == snapshot["zone_type"]
            and aliases.get(zone.pattern_type or "UNKNOWN", zone.pattern_type)
            == snapshot["pattern"]
            and abs(zone.lower_price - low) <= 1e-6
            and abs(zone.upper_price - high) <= 1e-6
        ]
        return max(candidates, key=lambda zone: zone.created_index) if candidates else None

    @staticmethod
    def _unavailable(snapshot: dict[str, Any], reason: str) -> dict[str, Any]:
        return {
            "zone_id": snapshot["zone_id"],
            "symbol": snapshot["symbol"],
            "timeframe": snapshot["timeframe"],
            "planning_timestamp": snapshot["planning_timestamp"],
            "zone_quality": {"status": "UNAVAILABLE", "reason": reason},
            "trade_confidence": {"status": "UNAVAILABLE", "reason": reason},
        }
