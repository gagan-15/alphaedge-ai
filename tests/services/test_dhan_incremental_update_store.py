from datetime import datetime
from pathlib import Path
from concurrent.futures import Future
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi import HTTPException

from backend.api import scanner as scanner_api
from backend.services.market_data.dhan_incremental_update_service import (
    DhanIncrementalUpdateService,
    latest_completed_nse_session,
)
from backend.data_providers.dhan import DhanInstrument
from backend.services.market_data.dhan_shadow_store import DhanShadowStore
from backend.services.market_data.dhan_dashboard_enrichment_service import (
    DhanDashboardEnrichmentService,
)


@pytest.mark.parametrize("worker_active", [False, True])
def test_runtime_status_checks_worker_without_mutating_run(tmp_path: Path, worker_active: bool) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")
    run_id = store.begin_incremental_update_run()
    with patch.object(scanner_api, "_dhan_shadow_store", store), patch.object(
        scanner_api, "_dhan_update_future", None
    ), patch.object(store, "dashboard_snapshot_statuses", return_value={"1D": {"status": "READY"}}), patch(
        "backend.services.market_data.update_process_lock.update_process_is_active",
        return_value=worker_active,
    ):
        response = scanner_api.get_dhan_runtime_status()
    assert response["data_status"] == ("UPDATING" if worker_active else "READY")
    assert response["last_update"]["status"] == ("RUNNING" if worker_active else "FAILED")
    assert store.incremental_update_status()["status"] == "RUNNING"
    assert store.incremental_update_status()["run_id"] == run_id


def test_recovery_reuses_canonical_until_source_revision(tmp_path: Path) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")
    instrument = DhanInstrument("NSE", "1", "FIRST", "INE000000001", "EQ", "NSE_MAIN", "First")
    store.synchronize_master((instrument,))
    candles = pd.DataFrame({"Open": [100.], "High": [102.], "Low": [99.], "Close": [101.], "Volume": [1000.]},
                           index=pd.DatetimeIndex(["2026-10-01"], tz="Asia/Kolkata"))
    store.merge(instrument, "1D", "1D", candles, semantics="test")
    cohort = "dhan_all_supported_indian_equity"
    store.save_canonical(cohort, instrument, "1D", [])
    with store.connection() as connection:
        connection.execute("UPDATE dhan_canonical_checkpoints SET updated_at='2026-10-02T12:00:00+00:00'")
        connection.execute("UPDATE dhan_shadow_candles SET retrieved_at='2026-10-02T10:00:00+00:00'")
        connection.commit()
    service = DhanIncrementalUpdateService(store=store)
    with patch.object(service, "_detect_with_watchdog", side_effect=AssertionError("must reuse")), patch.object(
        service, "_recompute_timeframe_parallel", side_effect=AssertionError("must reuse")
    ):
        assert service._recompute_timeframe("1D", {"NSE:1": instrument}, {"NSE:1": "2026-10-01"}) == ["NSE:1"]
    with store.connection() as connection:
        connection.execute("UPDATE dhan_shadow_candles SET retrieved_at='2026-10-02T13:00:00+00:00'")
        connection.commit()
    assert not store.canonical_covers_persisted_source(cohort, "NSE:1", "1D")
    assert not store.canonical_covers_persisted_source(cohort, "NSE:1", "1W")


def test_dashboard_result_identity_distinguishes_legacy_zone_id_collision() -> None:
    first = SimpleNamespace(
        zone_id="ZONE-AB292D75C8223213894B",
        zone_type="SUPPLY",
        pattern_type="RBD",
        base_index=139,
        base_date="2019-02-08",
        proximal_price=45.33,
        distal_price=47.33,
    )
    second = SimpleNamespace(
        zone_id="ZONE-AB292D75C8223213894B",
        zone_type="DEMAND",
        pattern_type="RBR",
        base_index=139,
        base_date="2017-03-14",
        proximal_price=15.33,
        distal_price=15.07,
    )

    assert DhanDashboardEnrichmentService._result_row_id(
        "BSE:500052", first,
    ) != DhanDashboardEnrichmentService._result_row_id("BSE:500052", second)


def test_persisted_resume_uses_shared_stages_without_provider_calls(tmp_path: Path) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")
    store.mark_incremental_dirty("NSE:1", "1D", "SOURCE_CHANGED", "2026-10-01")
    service = DhanIncrementalUpdateService(store=store)
    instrument = DhanInstrument("NSE", "1", "FIRST", "INE000000001", "EQ", "NSE_MAIN", "First")
    with patch.object(service.provider, "_ensure_client_id", side_effect=AssertionError("no auth")), patch.object(
        service.shadow, "sync_master", side_effect=AssertionError("no master download")
    ), patch.object(service, "_refresh_daily_candles", side_effect=AssertionError("no candle fetch")), patch.object(
        service, "_instrument_map", return_value={"NSE:1": instrument}
    ), patch.object(service, "_recompute_timeframe", return_value=["NSE:1"]) as compute, patch.object(
        service.enrichment, "refresh_affected_instruments"
    ) as enrich:
        report = service.run(resume_persisted=True)
    assert report.status == "READY"
    assert [call.args[0] for call in compute.call_args_list] == ["1D", "1W", "1M", "3M", "6M", "1Y"]
    assert enrich.call_count == 6
    assert store.incremental_update_status()["status"] == "READY"


def test_isolated_canonical_watchdog_returns_without_database_side_effects(
    tmp_path: Path,
) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")
    service = DhanIncrementalUpdateService(store=store)
    index = pd.date_range("2026-08-01", periods=8, freq="D", tz="Asia/Kolkata")
    candles = pd.DataFrame(
        {
            "Open": range(100, 108), "High": range(101, 109),
            "Low": range(99, 107), "Close": range(100, 108),
            "Volume": [1000] * 8,
        },
        index=index,
    )

    zones, elapsed, result = service._detect_with_watchdog(
        candles, timeout_seconds=30, should_cancel=None,
    )

    assert result == "SUCCESS"
    assert zones is not None
    assert elapsed >= 0


def test_pathological_diagnostic_is_persisted_without_credentials(
    tmp_path: Path,
) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")
    store.record_pathological_instrument(
        run_id=7, instrument_id="NSE:3761", timeframe="1D",
        symbol="RITES", candle_count=2023, zone_count=124,
        stage="CANONICAL_ZONE_DETECTION", elapsed_seconds=301.5,
        attempt=1, result="TIMEOUT",
    )
    with store.connection() as connection:
        row = connection.execute(
            "SELECT * FROM dhan_incremental_pathological_instruments"
        ).fetchone()

    assert row is not None
    assert row["instrument_id"] == "NSE:3761"
    assert row["result"] == "TIMEOUT"


def test_incremental_update_lock_prevents_duplicate_runs(tmp_path: Path) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")

    first = store.begin_incremental_update_run()
    assert first is not None
    assert store.begin_incremental_update_run() is None

    store.finish_incremental_update_run(
        first,
        status="READY",
        instruments_checked=3,
        instruments_changed=1,
        instruments_failed=0,
    )
    status = store.incremental_update_status()
    assert status["status"] == "READY"
    assert status["instruments_checked"] == 3
    assert status["instruments_changed"] == 1


def test_incremental_update_cancellation_is_bound_to_exact_active_run(tmp_path: Path) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")
    successful_run = store.begin_incremental_update_run()
    assert successful_run is not None
    store.finish_incremental_update_run(
        successful_run,
        status="READY",
        instruments_checked=1,
        instruments_changed=0,
        instruments_failed=0,
    )
    run_id = store.begin_incremental_update_run()
    assert run_id is not None
    assert store.request_incremental_update_cancellation(run_id + 1) is False
    assert store.request_incremental_update_cancellation(run_id) is True
    assert store.incremental_update_cancellation_requested(run_id) is True
    assert store.begin_incremental_update_run() is None

    store.finish_incremental_update_run(
        run_id,
        status="CANCELLED",
        instruments_checked=4,
        instruments_changed=1,
        instruments_failed=0,
        error="CANCELLED_BY_USER",
    )
    status = store.incremental_update_status()
    assert status["status"] == "CANCELLED"
    assert status["stage"] == "Update cancelled"
    assert store.latest_successful_incremental_update_at() is not None
    assert store.begin_incremental_update_run() is not None


def test_incremental_dirty_identity_is_resumable(tmp_path: Path) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")
    store.mark_incremental_dirty("NSE:1", "1D", "NEW_OR_REVISED_DHAN_DAILY_SESSION")
    store.mark_incremental_dirty("NSE:1", "1W", "DAILY_SOURCE_CHANGED")

    assert store.dirty_incremental_instruments("1D") == ["NSE:1"]
    assert store.dirty_incremental_instruments("1W") == ["NSE:1"]
    store.clear_incremental_dirty(["NSE:1"], "1D")
    assert store.dirty_incremental_instruments("1D") == []
    assert store.dirty_incremental_instruments("1W") == ["NSE:1"]


def test_incremental_update_can_scope_to_exact_active_dhan_identities(
    tmp_path: Path,
) -> None:
    """Stale-series repair must not traverse unrelated persisted symbols."""
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")

    class Shadow:
        def persisted_daily_canonical_universe(self, cohort: str):
            assert cohort == "dhan_all_supported_indian_equity"
            return (
                DhanInstrument(
                    "NSE", "1", "FIRST", "INE000000001", "EQ", "NSE_MAIN", "First"
                ),
                DhanInstrument(
                    "NSE", "2", "SECOND", "INE000000002", "EQ", "NSE_MAIN", "Second"
                ),
            )

    service = DhanIncrementalUpdateService(store=store)
    service.shadow = Shadow()  # type: ignore[assignment]

    assert list(service._instrument_map({"NSE:2"})) == ["NSE:2"]
    assert list(service._instrument_map()) == ["NSE:1", "NSE:2"]


def test_in_progress_monday_session_is_not_a_completed_daily_candle() -> None:
    """NSE dates must be evaluated in Asia/Kolkata, never UTC/host local time."""
    assert latest_completed_nse_session(
        datetime.fromisoformat("2026-08-31T13:25:00+05:30")
    ).isoformat() == "2026-08-28"


def test_post_close_monday_becomes_the_completed_daily_session() -> None:
    assert latest_completed_nse_session(
        datetime.fromisoformat("2026-08-31T15:31:00+05:30")
    ).isoformat() == "2026-08-31"


def test_incremental_update_progress_is_shared_durably(tmp_path: Path) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")
    run_id = store.begin_incremental_update_run()
    assert run_id is not None

    store.set_incremental_update_progress(
        run_id,
        stage="Recalculating affected instruments (1D)...",
        completed=12,
        total=37,
        affected_timeframes=("1D", "1W", "1M"),
    )

    status = store.incremental_update_status()
    assert status["stage"] == "Recalculating affected instruments (1D)..."
    assert status["progress_completed"] == 12
    assert status["progress_total"] == 37
    assert status["affected_timeframes"] == "1D,1W,1M"


def test_dashboard_update_endpoint_uses_shared_incremental_service(tmp_path: Path) -> None:
    previous_future = scanner_api._dhan_update_future
    future: Future[object] = Future()
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")
    try:
        scanner_api._dhan_update_future = None
        with patch.object(scanner_api, "MARKET_DATA_PROVIDER", "dhan"), patch.object(
            scanner_api, "DhanIncrementalUpdateService"
        ) as service, patch.object(scanner_api, "_dhan_shadow_store", store), patch.object(
            scanner_api._dhan_update_executor, "submit", return_value=future
        ) as submit:
            with pytest.raises(HTTPException, match="explicit user action"):
                scanner_api.start_dhan_incremental_update()
            response = scanner_api.start_dhan_incremental_update(
                x_alphaedge_update_intent="explicit-user",
            )
        assert response["status"] == "RUNNING"
        submit.assert_called_once()
        service.assert_called_once_with()
    finally:
        scanner_api._dhan_update_future = previous_future


def test_incremental_service_cancels_at_safe_boundary(tmp_path: Path) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")

    class Provider:
        def _ensure_client_id(self) -> str:
            return "safe-test-client"

    class Shadow:
        def sync_master(self) -> None:
            active = store.incremental_update_status()
            assert store.request_incremental_update_cancellation(int(active["run_id"]))

    service = DhanIncrementalUpdateService(provider=Provider(), store=store)  # type: ignore[arg-type]
    service.shadow = Shadow()  # type: ignore[assignment]
    report = service.run()

    assert report.status == "CANCELLED"
    assert store.incremental_update_status()["status"] == "CANCELLED"
    assert store.begin_incremental_update_run() is not None


def test_cancel_endpoint_targets_only_current_run(tmp_path: Path) -> None:
    store = DhanShadowStore(tmp_path / "dhan.sqlite3")
    run_id = store.begin_incremental_update_run()
    assert run_id is not None
    with patch.object(scanner_api, "_dhan_shadow_store", store):
        with pytest.raises(HTTPException, match="no longer active"):
            scanner_api.cancel_dhan_incremental_update(
                run_id + 1, x_alphaedge_update_intent="explicit-user"
            )
        response = scanner_api.cancel_dhan_incremental_update(
            run_id, x_alphaedge_update_intent="explicit-user"
        )
    assert response["status"] == "CANCELLING"
    assert response["run_id"] == run_id


def test_dhan_table_sort_aliases_are_normalized_before_querying() -> None:
    assert scanner_api._normalize_dhan_dashboard_sort("distance_percent") == "distance"
    assert scanner_api._normalize_dhan_dashboard_sort("zone_score") == "zone_quality"
    assert scanner_api._normalize_dhan_dashboard_sort("current_price") == "current_price"


def test_dhan_response_time_filters_and_sorting_use_rendered_values() -> None:
    rows = [
        {"symbol": "INZONE", "zone_id": "1", "status": "IN ZONE", "distance_percent": 0.0, "current_price": 191.45, "zone_score": 70.0},
        {"symbol": "NEAR", "zone_id": "2", "status": "APPROACHING", "distance_percent": 0.25, "current_price": 50.0, "zone_score": 80.0},
        {"symbol": "FAR", "zone_id": "3", "status": "FAR", "distance_percent": 9.0, "current_price": 300.0, "zone_score": 60.0},
    ]
    in_zone = scanner_api._filter_dhan_response_time_rows(
        rows, status="IN ZONE", max_distance=None,
    )
    approaching = scanner_api._filter_dhan_response_time_rows(
        rows, status="APPROACHING", max_distance=None,
    )
    far = scanner_api._filter_dhan_response_time_rows(
        rows, status="WATCH", max_distance=None,
    )
    within_five = scanner_api._filter_dhan_response_time_rows(
        rows, status=None, max_distance=5.0,
    )

    assert [row["symbol"] for row in in_zone] == ["INZONE"]
    assert [row["symbol"] for row in approaching] == ["NEAR"]
    assert [row["symbol"] for row in far] == ["FAR"]
    assert [row["symbol"] for row in within_five] == ["INZONE", "NEAR"]
    assert [row["symbol"] for row in scanner_api._sort_dhan_response_time_rows(
        rows, field="distance", descending=False,
    )] == ["INZONE", "NEAR", "FAR"]
    assert [row["symbol"] for row in scanner_api._sort_dhan_response_time_rows(
        rows, field="current_price", descending=True,
    )] == ["FAR", "INZONE", "NEAR"]
