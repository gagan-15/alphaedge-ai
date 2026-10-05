"""Resume legacy Run 6 after its in-process Daily calculation stalled.

This operation performs no provider calls and downloads no candles.  It trusts
the persisted Run 6 progress boundary, preserves completed canonical output,
and resumes only the remaining work with pathological-instrument protection.
"""

from __future__ import annotations

from backend.services.market_data.dhan_incremental_update_service import (
    DhanIncrementalUpdateService,
    IncrementalUpdateCancelled,
    _COHORT,
    _EOD_TIMEFRAMES,
)


RUN_ID = 6


def main() -> None:
    service = DhanIncrementalUpdateService()
    store = service.store
    status = store.incremental_update_status()
    if int(status.get("run_id") or 0) != RUN_ID:
        raise RuntimeError("Run 6 is not the current persisted update run.")
    if str(status.get("status")) != "RUNNING":
        raise RuntimeError("Run 6 is not resumable.")
    if str(status.get("stage")) != "Recalculating affected instruments (1D)...":
        raise RuntimeError("Run 6 is not at the verified Daily recovery stage.")

    dirty_daily = store.dirty_incremental_instruments("1D")
    completed_count = int(status.get("progress_completed") or 0)
    if completed_count <= 0 or completed_count >= len(dirty_daily):
        raise RuntimeError("Run 6 Daily recovery boundary is invalid.")

    instruments = service._instrument_map()
    completed_daily = dirty_daily[:completed_count]
    pathological_id = dirty_daily[completed_count]
    pathological = instruments.get(pathological_id)
    if pathological is None:
        raise RuntimeError("The verified pathological Dhan identity is unavailable.")
    if pathological_id != "NSE:3761":
        raise RuntimeError(
            f"Run 6 recovery expected NSE:3761, found {pathological_id}."
        )

    candles = store.load(pathological_id, "1D")
    prior_zones = len(
        store.active_structured_zone_payloads_for_instrument(
            _COHORT, "1D", pathological_id,
        )
    )
    store.record_pathological_instrument(
        run_id=RUN_ID, instrument_id=pathological_id, timeframe="1D",
        symbol=pathological.symbol, candle_count=len(candles),
        zone_count=prior_zones, stage="CANONICAL_ZONE_DETECTION",
        elapsed_seconds=0.0, attempt=1, result="LEGACY_RUN_STALLED",
    )
    # Preserve its last valid canonical/result state.  This exact Daily item is
    # terminal for Run 6 only and must not block the remaining cohort.
    store.clear_incremental_dirty([pathological_id], "1D")
    remaining_daily = dirty_daily[completed_count + 1:]

    def should_cancel() -> bool:
        return store.incremental_update_cancellation_requested(RUN_ID)

    def progress(frame: str):
        def update(completed: int, total: int) -> None:
            store.set_incremental_update_progress(
                RUN_ID,
                stage=f"Recalculating affected instruments ({frame})...",
                completed=completed, total=total,
                affected_timeframes=_EOD_TIMEFRAMES,
            )
        return update

    try:
        store.set_incremental_update_progress(
            RUN_ID, stage="Recalculating affected instruments (1D)...",
            completed=0, total=len(remaining_daily),
            affected_timeframes=_EOD_TIMEFRAMES,
        )
        resumed_daily = service._recompute_timeframe(
            "1D", instruments, remaining_daily, should_cancel,
            progress("1D"), RUN_ID,
        )
        changed_by_timeframe: dict[str, list[str]] = {
            "1D": [*completed_daily, *resumed_daily],
        }

        daily_source_changed = [*changed_by_timeframe["1D"], pathological_id]
        for timeframe in _EOD_TIMEFRAMES[1:]:
            for instrument_id in daily_source_changed:
                store.mark_incremental_dirty(
                    instrument_id, timeframe, "DAILY_SOURCE_CHANGED",
                )
            dirty = store.dirty_incremental_instruments(timeframe)
            store.set_incremental_update_progress(
                RUN_ID,
                stage=f"Recalculating affected instruments ({timeframe})...",
                completed=0, total=len(dirty),
                affected_timeframes=_EOD_TIMEFRAMES,
            )
            changed_by_timeframe[timeframe] = service._recompute_timeframe(
                timeframe, instruments, dirty, should_cancel,
                progress(timeframe), RUN_ID,
            )

        store.set_incremental_update_stage(
            RUN_ID, "Rebuilding affected timeframe results...",
        )
        refreshed: list[str] = []
        for timeframe, changed in changed_by_timeframe.items():
            if should_cancel():
                raise IncrementalUpdateCancelled
            if changed:
                service.enrichment.refresh_affected_instruments(
                    timeframe, changed, _COHORT,
                )
                store.clear_incremental_dirty(changed, timeframe)
                refreshed.append(timeframe)
        store.set_incremental_update_stage(RUN_ID, "Publishing READY snapshots...")
        store.finish_incremental_update_run(
            RUN_ID, status="READY", instruments_checked=len(instruments),
            instruments_changed=len(changed_by_timeframe["1D"]),
            instruments_failed=1,
        )
        print(
            f"Run 6 READY; resumed_daily={len(resumed_daily)}; "
            f"refreshed={','.join(refreshed)}",
            flush=True,
        )
    except IncrementalUpdateCancelled:
        store.finish_incremental_update_run(
            RUN_ID, status="CANCELLED", instruments_checked=len(instruments),
            instruments_changed=0, instruments_failed=1,
            error="CANCELLED_BY_USER",
        )
        raise
    except Exception as error:
        store.finish_incremental_update_run(
            RUN_ID, status="FAILED", instruments_checked=len(instruments),
            instruments_changed=0, instruments_failed=2,
            error=type(error).__name__,
        )
        raise


if __name__ == "__main__":
    main()
