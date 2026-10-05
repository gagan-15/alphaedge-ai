"""Idempotent, Dhan-only EOD refresh orchestration.

This service never bootstraps history.  It downloads only a small correction
window, persists validated new/revised Daily sessions, and recomputes the
canonical/result layers for affected exact Dhan identities only.
"""

from __future__ import annotations

import os
import pickle
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from multiprocessing import get_context
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from time import monotonic
from typing import Callable, Collection
from zoneinfo import ZoneInfo

import pandas as pd

from backend.data_providers.dhan import DhanInstrument, DhanMarketDataProvider
from backend.data_providers.dhan.dhan_provider import DhanDataError
from backend.services.market_data.dhan_dashboard_enrichment_service import (
    DhanDashboardEnrichmentService,
)
from backend.services.market_data.dhan_shadow_service import DhanShadowService
from backend.services.market_data.dhan_shadow_store import DhanShadowStore
from backend.services.market_data.incremental_canonical_service import (
    IncrementalCanonicalService,
)
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.validators.market_data_validator import MarketDataValidator


_COHORT = "dhan_all_supported_indian_equity"
_EOD_TIMEFRAMES = ("1D", "1W", "1M", "3M", "6M", "1Y")
_NSE_TIMEZONE = ZoneInfo("Asia/Kolkata")
_NSE_CASH_CLOSE = time(15, 30)
_INCREMENTAL_WORKER_STORES: dict[str, DhanShadowStore] = {}


def _incremental_canonical_worker(
    path: str, cohort: str, timeframe: str, instrument_id: str,
    earliest_timestamp: str,
) -> tuple[str, str, object, float, int, int]:
    """Read/calculate in a child process; parent serializes all writes."""
    started = monotonic()
    try:
        store = _INCREMENTAL_WORKER_STORES.get(path)
        if store is None:
            store = DhanShadowStore(Path(path))
            _INCREMENTAL_WORKER_STORES[path] = store
        data = store.load(instrument_id, timeframe)
        prior = store.active_structured_zone_payloads_for_instrument(
            cohort, timeframe, instrument_id,
        )
        result = IncrementalCanonicalService().refresh_validated(
            data, prior, earliest_timestamp,
        )
        return (
            instrument_id, "SUCCESS", result.zones,
            monotonic() - started, len(data), len(prior),
        )
    except Exception as error:
        return (
            instrument_id, type(error).__name__, None,
            monotonic() - started, 0, 0,
        )


def _isolated_canonical_detection(data: object, output_path: str) -> None:
    """Run frozen canonical detection without database write side effects."""
    try:
        zones: list[object] = []
        for segment in MarketDataValidator.validate_segments(data).segments:
            zones.extend(ZoneDetectionEngine().detect_zones(segment))
        result: tuple[str, object] = ("SUCCESS", zones)
    except Exception as error:  # sanitized across the process boundary
        result = ("FAILED", type(error).__name__)
    with Path(output_path).open("wb") as output:
        pickle.dump(result, output, protocol=pickle.HIGHEST_PROTOCOL)


def latest_completed_nse_session(
    now: datetime | None = None,
) -> date:
    """Return the latest safely completed weekday in NSE local time.

    The Dhan historical endpoint can be requested on a live session, but an
    in-progress Daily bar must never be persisted as a completed session.  A
    provider holiday simply returns no candle; it is not fabricated here.
    """
    local_now = (now or datetime.now(_NSE_TIMEZONE)).astimezone(_NSE_TIMEZONE)
    candidate = local_now.date()
    if local_now.time() < _NSE_CASH_CLOSE:
        candidate -= timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate


@dataclass(frozen=True)
class IncrementalUpdateReport:
    status: str
    checked: int
    changed: int
    failed: int
    refreshed_timeframes: tuple[str, ...]
    message: str = ""


class IncrementalUpdateCancelled(Exception):
    """Internal signal raised only after a safe incremental work boundary."""


class DhanIncrementalUpdateService:
    """Safe EOD update path for Task Scheduler and the manual launcher."""

    def __init__(
        self,
        provider: DhanMarketDataProvider | None = None,
        store: DhanShadowStore | None = None,
    ) -> None:
        self.provider = provider or DhanMarketDataProvider()
        self.store = store or DhanShadowStore()
        self.shadow = DhanShadowService(provider=self.provider, store=self.store)
        self.enrichment = DhanDashboardEnrichmentService(self.store)
        self.incremental_canonical = IncrementalCanonicalService()

    def _instrument_map(
        self, instrument_ids: Collection[str] | None = None,
    ) -> dict[str, DhanInstrument]:
        """Return the full active cohort or one exact, persisted subset.

        The subset form is used by operational stale-series repair.  It still
        uses the identical incremental fetch, validation, canonical, and
        atomic-result paths; it merely avoids traversing known-current series.
        """
        selected = None if instrument_ids is None else set(instrument_ids)
        return {
            item.instrument_id: item
            for item in self.shadow.persisted_daily_canonical_universe(_COHORT)
            if selected is None or item.instrument_id in selected
        }

    def _refresh_daily_candles(
        self, instruments: dict[str, DhanInstrument], overlap_days: int,
        should_cancel: Callable[[], bool] | None = None,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> tuple[dict[str, str], int]:
        changed: dict[str, str] = {}
        failures = 0
        total = len(instruments)
        for completed, (instrument_id, instrument) in enumerate(
            instruments.items(), start=1
        ):
            if should_cancel is not None and should_cancel():
                raise IncrementalUpdateCancelled
            persisted = self.store.load(instrument_id, "1D")
            if persisted.empty:
                # This cannot be repaired safely by the incremental path.
                failures += 1
                continue
            start = persisted.index.max().date() - timedelta(days=overlap_days)
            completed_session = latest_completed_nse_session()
            try:
                update = self.provider.download_instrument_data(
                    instrument, start=start, end=completed_session, interval="1d",
                )
                # Defend against a provider returning a current partial bar in
                # spite of the completed-session request boundary.
                update = update[update.index.date <= completed_session]
                if update.empty:
                    continue
                comparable_columns = ["Open", "High", "Low", "Close", "Volume"]
                persisted_by_stamp = {
                    pd.Timestamp(stamp).isoformat(): row
                    for stamp, row in persisted.iterrows()
                }
                changed_stamps: list[pd.Timestamp] = []
                for stamp, row in update.iterrows():
                    key = pd.Timestamp(stamp).isoformat()
                    previous = persisted_by_stamp.get(key)
                    if previous is None or any(
                        not self._same_number(previous.get(column), row.get(column))
                        for column in comparable_columns
                    ):
                        changed_stamps.append(pd.Timestamp(stamp))
                merged = self.store.merge(
                    instrument, "1D", "1d", update,
                    semantics=self.provider.source_semantics_version,
                )
                if merged.inserted or merged.corrected:
                    earliest = min(changed_stamps).isoformat()
                    self.store.mark_incremental_dirty(
                        instrument_id, "1D", "NEW_OR_REVISED_DHAN_DAILY_SESSION",
                        earliest,
                    )
                    changed[instrument_id] = earliest
            except Exception:
                # One unavailable instrument must not prevent a later READY
                # snapshot.  Existing canonical/result snapshots remain live.
                failures += 1
            finally:
                if on_progress is not None and (
                    completed == total or completed % 10 == 0
                ):
                    on_progress(completed, total)
        return changed, failures

    @staticmethod
    def _same_number(left: object, right: object) -> bool:
        if pd.isna(left) and pd.isna(right):
            return True
        try:
            return float(left) == float(right)
        except (TypeError, ValueError):
            return left == right

    def _detect_with_watchdog(
        self, data: object, timeout_seconds: float,
        should_cancel: Callable[[], bool] | None,
    ) -> tuple[list[object] | None, float, str]:
        """Isolate pure zone detection so one calculation can be terminated safely."""
        descriptor, output_path = tempfile.mkstemp(
            prefix="alphaedge-canonical-", suffix=".pickle",
        )
        os.close(descriptor)
        process = get_context("spawn").Process(
            target=_isolated_canonical_detection,
            args=(data, output_path),
            daemon=True,
        )
        started = monotonic()
        try:
            process.start()
            deadline = started + timeout_seconds
            while process.is_alive() and monotonic() < deadline:
                process.join(timeout=1.0)
                if should_cancel is not None and should_cancel():
                    process.terminate()
                    process.join(timeout=10)
                    raise IncrementalUpdateCancelled
            elapsed = monotonic() - started
            if process.is_alive():
                process.terminate()
                process.join(timeout=10)
                return None, elapsed, "TIMEOUT"
            if process.exitcode != 0:
                return None, elapsed, "ISOLATED_PROCESS_FAILED"
            with Path(output_path).open("rb") as source:
                status, payload = pickle.load(source)
            if status != "SUCCESS":
                return None, elapsed, str(payload)
            return list(payload), elapsed, "SUCCESS"
        finally:
            try:
                Path(output_path).unlink(missing_ok=True)
            except OSError:
                pass

    def _recompute_timeframe(
        self, timeframe: str, instruments: dict[str, DhanInstrument],
        dirty: dict[str, str | None] | list[str],
        should_cancel: Callable[[], bool] | None = None,
        on_progress: Callable[[int, int], None] | None = None,
        run_id: int = 0,
    ) -> list[str]:
        """Refresh canonical evidence with isolated pathological-item retries."""
        changed: list[str] = []
        deferred: list[tuple[DhanInstrument, object, int, int]] = []
        work = dirty if isinstance(dirty, dict) else {item: None for item in dirty}
        total = len(work)
        incremental_enabled = os.getenv(
            "ALPHAEDGE_INCREMENTAL_CANONICAL_ENABLED", "1"
        ).strip().lower() in {"1", "true", "yes"}
        # Interrupted runs leave dirty rows until result publication. Their
        # canonical writes may already be committed: reuse those exact rows,
        # but keep them in changed so result enrichment still finishes.
        reused = [identity for identity, earliest in work.items()
                  if earliest is not None and incremental_enabled
                  and self.store.canonical_covers_persisted_source(
                      _COHORT, identity, timeframe)]
        if reused:
            reused_set = set(reused)
            pending = {identity: earliest for identity, earliest in work.items()
                       if identity not in reused_set}
            if on_progress is not None:
                on_progress(len(reused), total)
            remaining = self._recompute_timeframe(
                timeframe, instruments, pending, should_cancel,
                (lambda done, count: on_progress(len(reused) + done, total))
                if on_progress is not None else None, run_id,
            ) if pending else []
            return reused + remaining
        if incremental_enabled and work and all(work.values()):
            return self._recompute_timeframe_parallel(
                timeframe, instruments, work, should_cancel, on_progress, run_id,
            )
        slow_seconds = max(
            1.0, float(os.getenv("ALPHAEDGE_SLOW_INSTRUMENT_SECONDS", "60")),
        )
        timeout_seconds = max(
            slow_seconds,
            float(os.getenv("ALPHAEDGE_INSTRUMENT_TIMEOUT_SECONDS", "300")),
        )
        retry_seconds = max(
            timeout_seconds,
            float(os.getenv("ALPHAEDGE_INSTRUMENT_RETRY_TIMEOUT_SECONDS", "900")),
        )
        for completed, (instrument_id, earliest_timestamp) in enumerate(
            work.items(), start=1,
        ):
            if should_cancel is not None and should_cancel():
                raise IncrementalUpdateCancelled
            instrument = instruments.get(instrument_id)
            if instrument is None:
                raise RuntimeError(
                    f"Current Dhan identity unavailable: {instrument_id}"
                )
            if timeframe != "1D":
                if earliest_timestamp is None:
                    self.shadow.materialize_eod(instrument, timeframe)
                else:
                    self.shadow.materialize_eod_suffix(
                        instrument, timeframe, earliest_timestamp,
                    )
            data = self.store.load(instrument_id, timeframe)
            prior_zone_count = len(
                self.store.active_structured_zone_payloads_for_instrument(
                    _COHORT, timeframe, instrument_id,
                )
            )
            zones = None
            elapsed = 0.0
            result = "FULL_REFERENCE_FALLBACK"
            if earliest_timestamp is not None and incremental_enabled:
                started = monotonic()
                try:
                    prior = self.store.active_structured_zone_payloads_for_instrument(
                        _COHORT, timeframe, instrument_id,
                    )
                    incremental = self.incremental_canonical.refresh_validated(
                        data, prior, earliest_timestamp,
                    )
                    zones = incremental.zones
                    result = "INCREMENTAL_SUCCESS"
                except Exception:
                    # Exactness is fail-closed: any unavailable/malformed prior
                    # state falls back for this identity only.
                    zones = None
                    result = "INCREMENTAL_FALLBACK"
                elapsed = monotonic() - started
            if zones is None:
                zones, elapsed, result = self._detect_with_watchdog(
                    data, timeout_seconds, should_cancel,
                )
            if zones is None:
                deferred.append((instrument, data, len(data), prior_zone_count))
                self.store.record_pathological_instrument(
                    run_id=run_id, instrument_id=instrument_id,
                    timeframe=timeframe, symbol=instrument.symbol,
                    candle_count=len(data), zone_count=prior_zone_count,
                    stage="CANONICAL_ZONE_DETECTION", elapsed_seconds=elapsed,
                    attempt=1, result=result,
                )
            else:
                self.store.save_canonical(_COHORT, instrument, timeframe, zones)
                changed.append(instrument_id)
                if elapsed >= slow_seconds:
                    self.store.record_pathological_instrument(
                        run_id=run_id, instrument_id=instrument_id,
                        timeframe=timeframe, symbol=instrument.symbol,
                        candle_count=len(data), zone_count=len(zones),
                        stage="CANONICAL_ZONE_DETECTION",
                        elapsed_seconds=elapsed, attempt=1,
                        result="SLOW_COMPLETED",
                    )
            if on_progress is not None and (
                completed == total or completed % 10 == 0
            ):
                on_progress(completed, total)

        # Retry only deferred calculations after the healthy cohort has moved on.
        for instrument, data, candle_count, prior_zone_count in deferred:
            zones, elapsed, result = self._detect_with_watchdog(
                data, retry_seconds, should_cancel,
            )
            if zones is not None:
                self.store.save_canonical(_COHORT, instrument, timeframe, zones)
                changed.append(instrument.instrument_id)
                retry_result = "RECOVERED"
                zone_count = len(zones)
            else:
                # Preserve the last valid canonical/result state and record an
                # explicit terminal update failure; never publish partial data.
                self.store.clear_incremental_dirty(
                    [instrument.instrument_id], timeframe,
                )
                retry_result = f"FAILED_PERMANENT:{result}"
                zone_count = prior_zone_count
            self.store.record_pathological_instrument(
                run_id=run_id, instrument_id=instrument.instrument_id,
                timeframe=timeframe, symbol=instrument.symbol,
                candle_count=candle_count, zone_count=zone_count,
                stage="CANONICAL_ZONE_DETECTION", elapsed_seconds=elapsed,
                attempt=2, result=retry_result,
            )
        return changed

    def _recompute_timeframe_parallel(
        self, timeframe: str, instruments: dict[str, DhanInstrument],
        work: dict[str, str | None],
        should_cancel: Callable[[], bool] | None,
        on_progress: Callable[[int, int], None] | None,
        run_id: int,
    ) -> list[str]:
        """Bounded CPU workers with one parent-side SQLite writer."""
        jobs: list[tuple[str, str, str, str, str]] = []
        for instrument_id, earliest in work.items():
            if should_cancel is not None and should_cancel():
                raise IncrementalUpdateCancelled
            instrument = instruments.get(instrument_id)
            if instrument is None or earliest is None:
                raise RuntimeError(f"Incremental state unavailable: {instrument_id}")
            if timeframe != "1D":
                self.shadow.materialize_eod_suffix(
                    instrument, timeframe, earliest,
                )
            jobs.append(
                (str(self.store.path), _COHORT, timeframe, instrument_id, earliest)
            )
        workers = max(1, min(8, int(os.getenv("ALPHAEDGE_EOD_WORKERS", "8"))))
        changed: list[str] = []
        columns = list(zip(*jobs))
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for completed, result in enumerate(
                pool.map(_incremental_canonical_worker, *columns, chunksize=4),
                start=1,
            ):
                if should_cancel is not None and should_cancel():
                    pool.shutdown(wait=True, cancel_futures=True)
                    raise IncrementalUpdateCancelled
                instrument_id, status, zones, elapsed, candles, prior_zones = result
                instrument = instruments[instrument_id]
                if status != "SUCCESS" or zones is None:
                    # Exact fail-closed fallback remains isolated to one identity.
                    data = self.store.load(instrument_id, timeframe)
                    zones, fallback_elapsed, fallback_status = self._detect_with_watchdog(
                        data,
                        float(os.getenv("ALPHAEDGE_INSTRUMENT_TIMEOUT_SECONDS", "300")),
                        should_cancel,
                    )
                    elapsed += fallback_elapsed
                    status = f"FALLBACK_{fallback_status}"
                if zones is None:
                    self.store.record_pathological_instrument(
                        run_id=run_id, instrument_id=instrument_id,
                        timeframe=timeframe, symbol=instrument.symbol,
                        candle_count=candles, zone_count=prior_zones,
                        stage="INCREMENTAL_CANONICAL", elapsed_seconds=elapsed,
                        attempt=1, result=status,
                    )
                else:
                    self.store.save_canonical(
                        _COHORT, instrument, timeframe, list(zones),
                    )
                    changed.append(instrument_id)
                if on_progress is not None and (
                    completed == len(jobs) or completed % 10 == 0
                ):
                    on_progress(completed, len(jobs))
        return changed

    def run(
        self,
        *,
        overlap_days: int = 7,
        instrument_ids: Collection[str] | None = None,
        resume_persisted: bool = False,
    ) -> IncrementalUpdateReport:
        from backend.services.market_data.update_process_lock import update_process_lock

        with update_process_lock(self.store.path) as acquired:
            if not acquired:
                return IncrementalUpdateReport(
                    "ALREADY_RUNNING", 0, 0, 0, (), "Another Dhan update is active."
                )
            return self._run_owned(
                overlap_days=overlap_days, instrument_ids=instrument_ids,
                resume_persisted=resume_persisted,
            )

    def _run_owned(
        self,
        *,
        overlap_days: int = 7,
        instrument_ids: Collection[str] | None = None,
        resume_persisted: bool = False,
    ) -> IncrementalUpdateReport:
        """Run once, or exit safely if a scheduler/manual run is already active."""
        if overlap_days < 1 or overlap_days > 14:
            raise ValueError(
                "Dhan correction overlap must be between 1 and 14 days."
            )
        # Only the exclusive OS-lock owner may recover an interrupted DB run.
        # A live owner cannot be displaced merely because six hours elapsed.
        run_id = self.store.begin_incremental_update_run(stale_after_seconds=0)
        if run_id is None:
            return IncrementalUpdateReport(
                "ALREADY_RUNNING", 0, 0, 0, (), "Another Dhan update is active."
            )

        checked = changed_count = failures = 0
        refreshed: list[str] = []
        try:
            def should_cancel() -> bool:
                return self.store.incremental_update_cancellation_requested(run_id)

            if should_cancel():
                raise IncrementalUpdateCancelled
            self.store.set_incremental_update_stage(
                run_id, "Authenticating Dhan..."
            )
            # Fail the complete run early on invalid Dhan credentials.  This
            # guarantees an HTTP 401 never looks like a successful no-op.
            if not resume_persisted:
                self.provider._ensure_client_id()
            # Master sync changes only the identity metadata; it does not
            # download history or modify canonical methodology.
            self.store.set_incremental_update_stage(
                run_id, "Checking latest market data..."
            )
            if not resume_persisted:
                self.shadow.sync_master()
            if should_cancel():
                raise IncrementalUpdateCancelled
            requested_instruments = (
                None if instrument_ids is None else set(instrument_ids)
            )
            instruments = self._instrument_map(requested_instruments)
            checked = len(instruments)
            if requested_instruments is not None and not instruments:
                self.store.finish_incremental_update_run(
                    run_id, status="READY", instruments_checked=0,
                    instruments_changed=0, instruments_failed=0,
                )
                return IncrementalUpdateReport(
                    "READY", 0, 0, 0, (),
                    "No active persisted Dhan instruments matched the repair scope.",
                )
            self.store.set_incremental_update_progress(
                run_id, stage="Downloading changed candles...", completed=0,
                total=checked,
            )
            newly_changed, failures = ({}, 0) if resume_persisted else self._refresh_daily_candles(
                instruments, overlap_days, should_cancel,
                lambda completed, total: self.store.set_incremental_update_progress(
                    run_id,
                    stage="Downloading changed candles...",
                    completed=completed, total=total,
                ),
            )
            dirty_daily = self.store.dirty_incremental_work("1D")
            dirty_daily.update(newly_changed)
            if requested_instruments is not None:
                dirty_daily = {
                    identity: stamp for identity, stamp in dirty_daily.items()
                    if identity in instruments
                }
            dirty_daily = dict(sorted(dirty_daily.items()))
            if not dirty_daily:
                self.store.finish_incremental_update_run(
                    run_id, status="READY", instruments_checked=checked,
                    instruments_changed=0, instruments_failed=failures,
                )
                return IncrementalUpdateReport(
                    "READY", checked, 0, failures, (),
                    "No new or revised Dhan sessions.",
                )

            changed_by_timeframe: dict[str, list[str]] = {}
            # A changed Daily session safely propagates to every maintained
            # EOD timeframe; this is operational metadata only.
            recalculation_frames = _EOD_TIMEFRAMES
            self.store.set_incremental_update_stage(
                run_id, "Validating and persisting candles..."
            )
            self.store.set_incremental_update_progress(
                run_id,
                stage="Recalculating affected instruments (1D)...",
                completed=0,
                total=len(dirty_daily),
                affected_timeframes=recalculation_frames,
            )
            changed_by_timeframe["1D"] = self._recompute_timeframe(
                "1D", instruments, dirty_daily, should_cancel,
                lambda completed, total: self.store.set_incremental_update_progress(
                    run_id,
                    stage="Recalculating affected instruments (1D)...",
                    completed=completed,
                    total=total,
                    affected_timeframes=recalculation_frames,
                ),
                run_id,
            )
            for timeframe in _EOD_TIMEFRAMES[1:]:
                if should_cancel():
                    raise IncrementalUpdateCancelled
                for instrument_id in changed_by_timeframe["1D"]:
                    self.store.mark_incremental_dirty(
                        instrument_id, timeframe, "DAILY_SOURCE_CHANGED",
                        dirty_daily.get(instrument_id),
                    )
                dirty = self.store.dirty_incremental_work(timeframe)
                if requested_instruments is not None:
                    dirty = {
                        instrument_id: stamp
                        for instrument_id, stamp in dirty.items()
                        if instrument_id in instruments
                    }
                self.store.set_incremental_update_progress(
                    run_id,
                    stage=f"Recalculating affected instruments ({timeframe})...",
                    completed=0,
                    total=len(dirty),
                    affected_timeframes=recalculation_frames,
                )

                def on_timeframe_progress(
                    completed: int, total: int, frame: str = timeframe,
                ) -> None:
                    self.store.set_incremental_update_progress(
                        run_id,
                        stage=f"Recalculating affected instruments ({frame})...",
                        completed=completed,
                        total=total,
                        affected_timeframes=recalculation_frames,
                    )

                changed_by_timeframe[timeframe] = self._recompute_timeframe(
                    timeframe,
                    instruments,
                    dirty,
                    should_cancel,
                    on_timeframe_progress,
                    run_id,
                )

            # Publish replacements only after all changed canonical state is
            # valid. A failed result snapshot is never promoted over READY.
            self.store.set_incremental_update_stage(
                run_id, "Rebuilding affected timeframe results..."
            )
            for timeframe, changed in changed_by_timeframe.items():
                if should_cancel():
                    raise IncrementalUpdateCancelled
                if changed:
                    self.enrichment.refresh_affected_instruments(
                        timeframe, changed, _COHORT
                    )
                    self.store.clear_incremental_dirty(changed, timeframe)
                    refreshed.append(timeframe)
            self.store.set_incremental_update_stage(
                run_id, "Publishing READY snapshots..."
            )
            changed_count = len(changed_by_timeframe["1D"])
        except IncrementalUpdateCancelled:
            self.store.finish_incremental_update_run(
                run_id, status="CANCELLED", instruments_checked=checked,
                instruments_changed=changed_count, instruments_failed=failures,
                error="CANCELLED_BY_USER",
            )
            return IncrementalUpdateReport(
                "CANCELLED", checked, changed_count, failures, tuple(refreshed),
                "Update cancelled. Existing READY snapshots remain active.",
            )
        except Exception as error:
            self.store.finish_incremental_update_run(
                run_id, status="FAILED", instruments_checked=checked,
                instruments_changed=changed_count, instruments_failed=failures + 1,
                error=(
                    f"DHAN_HTTP_{error.http_status}"
                    if isinstance(error, DhanDataError) and error.http_status
                    else type(error).__name__
                ),
            )
            return IncrementalUpdateReport(
                "FAILED", checked, changed_count, failures + 1,
                tuple(refreshed), type(error).__name__,
            )

        self.store.finish_incremental_update_run(
            run_id, status="READY", instruments_checked=checked,
            instruments_changed=changed_count, instruments_failed=failures,
        )
        return IncrementalUpdateReport(
            "READY", checked, changed_count, failures, tuple(refreshed)
        )
