"""Dhan-only persisted-zone Dashboard enrichment.

Formation is intentionally absent from this module.  It reads structured
canonical zones, strictly rehydrates them and hands them to the same
``ZoneResultEnrichmentService`` used by the live scanner.
"""

from __future__ import annotations

import json
import os
from hashlib import sha256
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from backend.api.models.scanner_response import CanonicalTradeConfidenceResponse
from backend.config.canonical_methodology import SCANNER_METHODOLOGY_CACHE_VERSION
from backend.config.gtf_workflow_roles import resolve_gtf_workflow
from backend.engines.trade_confidence_engine import CanonicalTradeConfidenceEngine
from backend.engines.trend_engine.canonical_trend_engine import CanonicalTrendEngine
from backend.models.canonical_zone_analysis import CanonicalZoneAnalysis
from backend.services.market_data.dhan_shadow_store import DhanShadowStore
from backend.services.market_data.dhan_zone_rehydration import (
    DhanZoneRehydrationError,
    rehydrate_zone,
)
from backend.services.market_data.timeframe_service import aggregate_timeframe
from backend.services.scanner.zone_result_enrichment_service import ZoneResultEnrichmentService


_TIMEFRAME_LABELS = {
    "15m": "15m", "75m": "75m", "125m": "125m", "1H": "1H",
    "1D": "1D", "1W": "1W", "1M": "1M", "3M": "3M", "6M": "6M", "1Y": "1Y",
}

_WORKER_SERVICES: dict[str, "DhanDashboardEnrichmentService"] = {}


def _enrich_affected_worker(
    path: str, cohort: str, timeframe: str, instrument_id: str,
) -> tuple[str, str, list[tuple]]:
    """Pure calculation/read worker; the parent owns every SQLite write."""
    service = _WORKER_SERVICES.get(path)
    if service is None:
        service = DhanDashboardEnrichmentService(DhanShadowStore(Path(path)))
        _WORKER_SERVICES[path] = service
    instrument = service.store.active_instrument_by_id(instrument_id)
    if instrument is None:
        return instrument_id, "ACTIVE_DHAN_INSTRUMENT_MISSING", []
    symbol, exchange = str(instrument["symbol"]), str(instrument["exchange"])
    try:
        payloads = service.store.active_structured_zone_payloads_for_instrument(
            cohort, timeframe, instrument_id,
        )
        zones = [
            rehydrate_zone(json.loads(str(row["payload"]))) for row in payloads
        ]
        candles = service.store.load(instrument_id, timeframe)
        if candles.empty:
            return instrument_id, "PERSISTED_DHAN_CANDLES_UNAVAILABLE", []
        batch = service._enrichment.enrich(
            zones=zones, data=candles, symbol=symbol, timeframe=timeframe,
        )
        confidence_context = service._confidence_context(timeframe, candles, symbol)
        rows: dict[str, tuple] = {}
        for item in batch.active:
            confidence = service._confidence_for(
                item, candles, context=confidence_context,
            )
            item = item.model_copy(update={"trade_confidence": confidence})
            row_id = service._result_row_id(instrument_id, item)
            rows[row_id] = (
                row_id, instrument_id, symbol, exchange, item.zone_type,
                item.pattern_type, item.zone_score, confidence.score,
                item.distance_percent, item.dashboard_qualified,
                item.model_dump_json(),
            )
        return instrument_id, "COMPLETE", list(rows.values())
    except Exception as error:
        return instrument_id, type(error).__name__, []


class DhanDashboardEnrichmentService:
    """Materialize source-isolated scanner rows from Dhan persistence only."""

    def __init__(self, store: DhanShadowStore) -> None:
        self.store = store
        self._enrichment = ZoneResultEnrichmentService()
        self._trend = CanonicalTrendEngine()
        self._confidence = CanonicalTradeConfidenceEngine()

    @staticmethod
    def _result_row_id(instrument_id: str, item: object) -> str:
        """Return a stable result identity without trusting abbreviated zone IDs.

        A legacy zone hash can collide for formations that share an instrument
        and local candle index.  Dashboard persistence therefore keys the row
        from the complete immutable formation/boundary identity instead.  This
        changes storage identity only; no analytical value is recalculated.
        """
        identity = json.dumps(
            {
                "instrument_id": instrument_id,
                "zone_id": getattr(item, "zone_id", None),
                "zone_type": str(getattr(item, "zone_type", "")),
                "pattern": str(getattr(item, "pattern_type", "")),
                "base_index": getattr(item, "base_index", None),
                "base_date": str(getattr(item, "base_date", "")),
                "proximal": getattr(item, "proximal_price", None),
                "distal": getattr(item, "distal_price", None),
            },
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return f"{instrument_id}:RESULT-{sha256(identity.encode('utf-8')).hexdigest()[:24]}"

    @staticmethod
    def _serialize_confidence(value: object) -> CanonicalTradeConfidenceResponse:
        return CanonicalTradeConfidenceResponse(
            score=value.total_score, label=value.label.value,
            zone_quality_score=value.zone_quality_score,
            zone_quality_contribution=value.zone_quality_contribution,
            location_contribution=value.location_contribution,
            trend_contribution=value.trend_contribution,
            location_alignment=value.location_alignment,
            trend_alignment=value.trend_alignment,
            combined_context=value.combined_context,
            htf_overlap_type=value.htf_overlap_type,
            htf_direction_compatibility=value.htf_direction_compatibility,
            data_sufficiency=value.data_sufficiency.value,
            reason_codes=value.reason_codes, evidence=value.evidence,
            shadow_mode=False,
        )

    def _confidence_context(self, timeframe, candles, symbol):
        """Calculate immutable per-instrument/timeframe context once."""
        workflow = resolve_gtf_workflow(timeframe)
        trend_frame = aggregate_timeframe(candles, workflow.trend) if workflow.trend else candles.iloc[0:0]
        trend = self._trend.evaluate(symbol, workflow.trend, trend_frame)
        return workflow, trend

    def _confidence_for(self, item, candles, *, context=None):
        """Use frozen TC math with Dhan candles and explicit unavailable HTF context."""
        workflow, trend = context or self._confidence_context(
            item.timeframe, candles, item.symbol,
        )
        alignment = self._trend.alignment(item.zone_type, trend.trend_state).value
        analysis = CanonicalZoneAnalysis(
            zone_id=item.zone_id or f"{item.symbol}:{item.base_index}", symbol=item.symbol,
            timeframe=item.timeframe, zone_type=item.zone_type, pattern=item.pattern_type,
            proximal=item.proximal_price, distal=item.distal_price,
            formation_evidence=None, lifecycle=None, authenticity=None,
            zone_quality=item.zone_score, canonical_trend=trend.as_dict(), htf_context=None,
            alignment=alignment, significant_gap=False, gap_measurement=None,
            trend_timeframe=workflow.trend, location_timeframe=workflow.location,
            trend_alignment=alignment, location_relationship="NO_OVERLAP",
            location_compatibility="NO_HTF_CONTEXT", combined_context="INSUFFICIENT_CONTEXT",
            data_sufficient=trend.data_sufficient,
            reason_codes=tuple(reason.value for reason in trend.reason_codes) + ("HTF_NO_ACTIVE_ZONE",),
        )
        return self._serialize_confidence(self._confidence.evaluate(analysis))

    def materialize(
        self, timeframe: str, cohort: str = "dhan_all_supported_indian_equity"
    ) -> dict[str, int | str]:
        """Build a resumable Dhan result snapshot without redetecting zones.

        ``timeframe`` must already have a completed canonical Dhan snapshot.
        This method only rehydrates that immutable output and runs the frozen
        downstream enrichment path; it never invokes formation detection.
        """
        if timeframe not in _TIMEFRAME_LABELS:
            raise ValueError(f"Unsupported Dhan timeframe: {timeframe}")
        instruments = self.store.active_canonical_instruments(cohort, timeframe)
        snapshot_id = self.store.latest_building_dashboard_result_snapshot(
            cohort, timeframe, SCANNER_METHODOLOGY_CACHE_VERSION,
        ) or self.store.begin_dashboard_result_snapshot(
            cohort, timeframe, len(instruments), methodology_version=SCANNER_METHODOLOGY_CACHE_VERSION,
        )
        payloads = defaultdict(list)
        for row in self.store.active_structured_zone_payloads(cohort, timeframe):
            payloads[str(row["instrument_id"])].append(row)
        processed = exclusions = result_count = typed_count = 0
        rows: dict[str, tuple] = {}
        for instrument in instruments:
            instrument_id, symbol, exchange = (str(instrument["instrument_id"]), str(instrument["symbol"]), str(instrument["exchange"]))
            if self.store.dashboard_checkpoint_complete(snapshot_id, instrument_id):
                processed += 1
                continue
            try:
                zones = [rehydrate_zone(json.loads(str(row["payload"]))) for row in payloads[instrument_id]]
                typed_count += len(zones)
                candles = self.store.load(instrument_id, timeframe)
                if candles.empty:
                    exclusions += 1
                    self.store.checkpoint_dashboard_result(snapshot_id, instrument_id, "TERMINAL_EXCLUSION", "PERSISTED_CANDLES_UNAVAILABLE")
                    processed += 1
                    continue
                batch = self._enrichment.enrich(
                    zones=zones, data=candles, symbol=symbol, timeframe=timeframe
                )
                confidence_context = self._confidence_context(
                    timeframe, candles, symbol,
                )
                for item in batch.active:
                    confidence = self._confidence_for(
                        item, candles, context=confidence_context,
                    )
                    item = item.model_copy(update={"trade_confidence": confidence})
                    row_id = self._result_row_id(instrument_id, item)
                    rows[row_id] = (row_id, instrument_id, symbol, exchange, item.zone_type, item.pattern_type,
                                    item.zone_score, confidence.score, item.distance_percent,
                                    item.dashboard_qualified, item.model_dump_json())
                    result_count += 1
            except (DhanZoneRehydrationError, KeyError, TypeError, ValueError):
                # Fail closed for a malformed active record.  It is deliberately
                # excluded from publication rather than parsed heuristically.
                exclusions += 1
                self.store.checkpoint_dashboard_result(snapshot_id, instrument_id, "TERMINAL_EXCLUSION", "STRICT_TYPED_REHYDRATION_FAILED")
            else:
                self.store.checkpoint_dashboard_result(snapshot_id, instrument_id, "COMPLETE")
            processed += 1
            if len(rows) >= 250:
                self.store.write_dashboard_result_rows(snapshot_id, list(rows.values()))
                rows.clear()
        self.store.write_dashboard_result_rows(snapshot_id, list(rows.values()))
        persisted_rows = self.store.dashboard_result_row_count(snapshot_id)
        self.store.publish_dashboard_result_snapshot(
            snapshot_id, processed=processed, results=persisted_rows, exclusions=exclusions,
        )
        return {"snapshot_id": snapshot_id, "processed": processed, "typed_zones": typed_count,
                "rows": persisted_rows, "exclusions": exclusions, "status": "READY"}

    def materialize_daily(
        self, cohort: str = "dhan_all_supported_indian_equity"
    ) -> dict[str, int | str]:
        """Backward-compatible Daily entry point."""
        return self.materialize("1D", cohort)

    def refresh_affected_instruments(
        self, timeframe: str, instrument_ids: list[str],
        cohort: str = "dhan_all_supported_indian_equity",
    ) -> dict[str, int | str]:
        """Atomically refresh result rows for changed Dhan instruments only.

        Canonical zones have already been recomputed from validated persisted
        candles by the caller.  This preserves the current READY snapshot until
        every affected instrument has passed strict rehydration and enrichment.
        """
        if timeframe not in _TIMEFRAME_LABELS:
            raise ValueError(f"Unsupported Dhan timeframe: {timeframe}")
        affected = sorted(set(instrument_ids))
        if not affected:
            source = self.store.latest_ready_dashboard_result_snapshot(cohort, timeframe)
            return {"snapshot_id": int(source["snapshot_id"]) if source else 0,
                    "processed": 0, "rows": 0, "status": "UNCHANGED"}
        source = self.store.latest_ready_dashboard_result_snapshot(cohort, timeframe)
        if source is None:
            raise RuntimeError(f"No READY Dhan Dashboard snapshot exists for {timeframe}.")
        target = self.store.begin_dashboard_result_snapshot(
            cohort, timeframe, int(source["total_instruments"]),
            methodology_version=str(source["methodology_version"]),
        )
        self.store.copy_dashboard_result_rows(int(source["snapshot_id"]), target)
        processed = 0
        replacements: dict[str, list[tuple]] = {}
        try:
            workers = max(1, min(8, int(os.getenv("ALPHAEDGE_EOD_WORKERS", "8"))))
            arguments = (
                (str(self.store.path), cohort, timeframe, instrument_id)
                for instrument_id in affected
            )
            with ProcessPoolExecutor(max_workers=workers) as pool:
                for instrument_id, status, rows in pool.map(
                    _enrich_affected_worker, *zip(*arguments), chunksize=4,
                ):
                    if status != "COMPLETE":
                        raise RuntimeError(
                            f"Dhan enrichment failed closed: {instrument_id}:{status}"
                        )
                    replacements[instrument_id] = rows
                    processed += 1
                    if len(replacements) >= 50:
                        self.store.replace_dashboard_instruments_rows(
                            target, replacements,
                        )
                        replacements.clear()
            self.store.replace_dashboard_instruments_rows(target, replacements)
        except Exception as error:
            self.store.abandon_dashboard_result_snapshot(target, type(error).__name__)
            raise
        result_count = self.store.dashboard_result_row_count(target)
        self.store.publish_dashboard_result_snapshot(
            target, processed=int(source["processed_instruments"]), results=result_count,
            exclusions=int(source["exclusion_count"]),
        )
        return {"snapshot_id": target, "processed": processed, "rows": result_count, "status": "READY"}

    def repair_daily_formation_anchors(
        self, cohort: str = "dhan_all_supported_indian_equity"
    ) -> dict[str, int | str]:
        """Atomically correct only result-row chart anchors from stored evidence.

        No candles are downloaded and no zone is detected.  This repairs a
        pre-anchor-schema result snapshot using the formation timestamps that
        were already persisted with each canonical zone.
        """
        source = self.store.latest_ready_dashboard_result_snapshot(cohort, "1D")
        if source is None:
            raise RuntimeError("No READY Dhan Daily Dashboard snapshot exists.")
        source_id = int(source["snapshot_id"])
        raw_by_key: dict[tuple[str, int, str, float, float], dict] = {}
        for raw in self.store.active_structured_zone_payloads(cohort, "1D"):
            payload = json.loads(str(raw["payload"]))
            key = (
                str(raw["instrument_id"]), int(payload["created_index"]),
                str(payload["zone_type"]), float(payload["upper_price"]),
                float(payload["lower_price"]),
            )
            raw_by_key[key] = payload
        replacements: dict[str, str] = {}
        with self.store.connection() as connection:
            rows = connection.execute(
                """SELECT row_id,instrument_id,payload FROM dhan_dashboard_result_rows
                WHERE snapshot_id=?""", (source_id,)
            ).fetchall()
        for row in rows:
            result = json.loads(str(row["payload"]))
            upper = max(float(result["proximal_price"]), float(result["distal_price"]))
            lower = min(float(result["proximal_price"]), float(result["distal_price"]))
            key = (str(row["instrument_id"]), int(result["base_index"]), str(result["zone_type"]), upper, lower)
            raw = raw_by_key.get(key)
            if raw is None:
                continue
            zone = rehydrate_zone(raw)
            evidence = zone.formation_evidence
            if evidence is None or not evidence.base_timestamps:
                continue
            anchor_index = evidence.base_start_index
            anchor_date = str(evidence.base_timestamps[0])[:10]
            if result["base_index"] != anchor_index or result["base_date"] != anchor_date:
                result["base_index"] = anchor_index
                result["base_date"] = anchor_date
                replacements[str(row["row_id"])] = json.dumps(result, separators=(",", ":"))
        target_id = self.store.begin_dashboard_result_snapshot(
            cohort, "1D", int(source["total_instruments"]),
            methodology_version=str(source["methodology_version"]),
        )
        self.store.copy_dashboard_result_rows(source_id, target_id)
        self.store.update_dashboard_result_payloads(target_id, replacements)
        self.store.publish_dashboard_result_snapshot(
            target_id, processed=int(source["processed_instruments"]),
            results=self.store.dashboard_result_row_count(target_id),
            exclusions=int(source["exclusion_count"]),
        )
        return {"source_snapshot_id": source_id, "snapshot_id": target_id,
                "repaired_rows": len(replacements), "status": "READY"}
