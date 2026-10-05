"""Milestone 12 durable scanner-storage regression locks."""

import sqlite3
import json
from pathlib import Path

from backend.api.models.scanner_response import ZoneResearchResponse
from backend.api.scanner import _merge_symbol_responses
from backend.services.scanner.persistent_scanner_store import (
    SCANNER_ARCHITECTURE_VERSION,
    SCANNER_STORAGE_VERSION,
    PersistentScannerStore,
)


def test_milestone_12_frozen_architecture_identity() -> None:
    assert SCANNER_ARCHITECTURE_VERSION == "persistent-all-nse-scanner-v1"
    assert SCANNER_STORAGE_VERSION == "milestone-12.2-resumable"


def response(*, zones: int = 0, timeframe: str = "1D") -> ZoneResearchResponse:
    return ZoneResearchResponse(
        total_scanned=2,
        total_zones=zones,
        timeframe=timeframe,
        results=(),
        universe="nse500",
        total_symbols=2,
        processed_symbols=2,
        failed_symbols=0,
        last_completed_at="2026-08-22T12:00:00+00:00",
    )


def test_complete_snapshot_survives_store_restart(tmp_path: Path) -> None:
    path = tmp_path / "scanner.sqlite3"
    first = PersistentScannerStore(path)
    snapshot_id = first.begin_snapshot(
        universe="nse500",
        timeframe="DAILY",
        methodology_version="formation-1.1",
        symbols=None,
        total_symbols=2,
    )
    first.publish(snapshot_id, response())

    restarted = PersistentScannerStore(path)
    stored = restarted.latest_complete(
        universe="nse500",
        timeframe="DAILY",
        methodology_version="formation-1.1",
        symbols=None,
    )

    assert stored is not None
    assert stored.response.total_scanned == 2
    assert stored.response.methodology_version == "formation-1.1"


def test_building_snapshot_never_replaces_last_known_good(tmp_path: Path) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    complete_id = store.begin_snapshot(
        universe="nse500",
        timeframe="DAILY",
        methodology_version="formation-1.1",
        symbols=None,
        total_symbols=2,
    )
    store.publish(complete_id, response(zones=3))
    store.begin_snapshot(
        universe="nse500",
        timeframe="DAILY",
        methodology_version="formation-1.1",
        symbols=None,
        total_symbols=2,
    )

    stored = store.latest_complete(
        universe="nse500",
        timeframe="DAILY",
        methodology_version="formation-1.1",
        symbols=None,
    )

    assert stored is not None
    assert stored.response.total_zones == 3


def test_failed_refresh_preserves_last_known_good(tmp_path: Path) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    complete_id = store.begin_snapshot(
        universe="nifty50",
        timeframe="WEEKLY",
        methodology_version="formation-1.1",
        symbols=None,
        total_symbols=50,
    )
    complete = response(zones=1).model_copy(update={
        "universe": "nifty50",
        "total_symbols": 50,
        "processed_symbols": 50,
    })
    store.publish(complete_id, complete)
    failed_id = store.begin_snapshot(
        universe="nifty50",
        timeframe="WEEKLY",
        methodology_version="formation-1.1",
        symbols=None,
        total_symbols=50,
    )
    store.fail(failed_id, "provider unavailable")

    stored = store.latest_complete(
        universe="nifty50",
        timeframe="WEEKLY",
        methodology_version="formation-1.1",
        symbols=None,
    )

    assert stored is not None
    assert stored.response.total_zones == 1
    assert store.status_counts() == {"COMPLETE": 1, "FAILED": 1}


def test_methodology_mismatch_is_not_returned(tmp_path: Path) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    snapshot_id = store.begin_snapshot(
        universe="nse500",
        timeframe="DAILY",
        methodology_version="formation-1.0",
        symbols=None,
        total_symbols=500,
    )
    store.publish(snapshot_id, response())

    assert store.latest_complete(
        universe="nse500",
        timeframe="DAILY",
        methodology_version="formation-1.1",
        symbols=None,
    ) is None


def test_exchange_identity_and_universe_membership_are_stable(tmp_path: Path) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    store.seed_universe("nifty50", ["RELIANCE", "TCS"], source="fixture")
    store.seed_universe("nse500", ["RELIANCE", "TCS", "INFY"], source="fixture")

    assert store.instrument_counts() == {"nifty50": 2, "nse500": 3}


def test_replacement_job_marks_interrupted_work_retryable(tmp_path: Path) -> None:
    path = tmp_path / "scanner.sqlite3"
    store = PersistentScannerStore(path)
    job_id = store.create_job("nse500", "DAILY", "formation-1.1", 500)
    store.update_job(job_id, "RUNNING", processed=417, failed=2)
    store.begin_snapshot(
        universe="nse500",
        timeframe="DAILY",
        methodology_version="formation-1.1",
        symbols=None,
        total_symbols=500,
    )

    restarted = PersistentScannerStore(path)
    # Opening the store is read-safe and must not steal a live worker lease.
    with sqlite3.connect(path) as connection:
        assert connection.execute(
            "SELECT status FROM scanner_jobs WHERE job_id=?", (job_id,)
        ).fetchone() == ("RUNNING",)
    restarted.create_job("nse500", "DAILY", "formation-1.1", 500)

    with sqlite3.connect(path) as connection:
        job = connection.execute(
            "SELECT status, processed_instruments FROM scanner_jobs WHERE job_id=?",
            (job_id,),
        ).fetchone()
        snapshot = connection.execute(
            "SELECT status FROM scanner_snapshots ORDER BY snapshot_id DESC LIMIT 1"
        ).fetchone()

    assert job == ("RETRYABLE", 417)
    assert snapshot == ("FAILED",)


def test_query_architecture_scales_beyond_five_thousand_rows(
    tmp_path: Path,
) -> None:
    """Synthetic infrastructure test; these are not market instruments."""

    path = tmp_path / "scanner.sqlite3"
    store = PersistentScannerStore(path)
    snapshot_id = store.begin_snapshot(
        universe="synthetic-scale",
        timeframe="DAILY",
        methodology_version="formation-1.1",
        symbols=None,
        total_symbols=5_500,
    )
    rows = []
    for index in range(5_500):
        zone_type = "DEMAND" if index % 2 == 0 else "SUPPLY"
        quality = float(index % 101)
        rows.append(
            (
                snapshot_id,
                f"zone-{index:05d}",
                f"NSE:SYN{index:05d}",
                "NSE",
                f"SYN{index:05d}",
                "1D",
                zone_type,
                "DROP_BASE_RALLY",
                quality,
                quality,
                "MODERATE",
                "FRESH",
                float(index % 20),
                100.0 + index,
                index + 1,
                f'{{"row":{index}}}',
            )
        )
    with sqlite3.connect(path) as connection:
        connection.executemany(
            """
            INSERT INTO scanner_result_rows(
                snapshot_id, zone_id, instrument_id, exchange, symbol,
                timeframe, zone_type, pattern, zone_quality,
                trade_confidence, trade_confidence_label, lifecycle_status,
                distance_percent, current_price, contextual_rank, row_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()

    total, page = store.query_results(
        snapshot_id,
        zone_type="DEMAND",
        min_zone_quality=80,
        sort="zone_quality",
        descending=True,
        page=2,
        page_size=50,
    )

    assert total > 500
    assert len(page) == 50


def test_global_sort_precedes_pagination_with_stable_tie_breakers(
    tmp_path: Path,
) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    snapshot_id = store.begin_snapshot(
        universe="allnse",
        timeframe="DAILY",
        methodology_version="formation-1.1",
        symbols=None,
        total_symbols=30,
    )
    rows = []
    for index in range(30):
        confidence = float((index * 17) % 11)
        quality = float((index * 13) % 9)
        distance = float((index * 7) % 8)
        zone_id = f"zone-{29 - index:02d}"
        payload = json.dumps({
            "zone_id": zone_id,
            "symbol": f"SYM{index:02d}",
            "trade_confidence": confidence,
            "zone_score": quality,
            "distance_percent": distance,
            "zone_type": "DEMAND" if index % 2 == 0 else "SUPPLY",
        })
        rows.append((
            snapshot_id, zone_id, f"NSE:SYM{index:02d}", "NSE", f"SYM{index:02d}",
            "1D", "DEMAND" if index % 2 == 0 else "SUPPLY", "DROP_BASE_RALLY",
            quality, confidence, "LOW", "FRESH", distance, 100.0 + index,
            30 - index, payload,
        ))
    with sqlite3.connect(store.path) as connection:
        connection.executemany(
            """
            INSERT INTO scanner_result_rows(
                snapshot_id, zone_id, instrument_id, exchange, symbol,
                timeframe, zone_type, pattern, zone_quality,
                trade_confidence, trade_confidence_label, lifecycle_status,
                distance_percent, current_price, contextual_rank, row_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()

    for sort, payload_key in (
        ("trade_confidence", "trade_confidence"),
        ("zone_quality", "zone_score"),
        ("distance", "distance_percent"),
    ):
        for descending in (False, True):
            concatenated: list[dict[str, object]] = []
            totals = set()
            for page_number in range(1, 5):
                total, page = store.query_results(
                    snapshot_id,
                    sort=sort,
                    descending=descending,
                    page=page_number,
                    page_size=10,
                )
                totals.add(total)
                concatenated.extend(json.loads(item) for item in page)
            expected = sorted(
                (json.loads(row[-1]) | {"contextual_rank": row[-2]} for row in rows),
                key=lambda item: (
                    -float(item[payload_key])
                    if descending
                    else float(item[payload_key]),
                    int(item["contextual_rank"]),
                    str(item["zone_id"]),
                ),
            )
            assert totals == {30}
            assert [item["zone_id"] for item in concatenated] == [
                item["zone_id"] for item in expected
            ]
            assert len({item["zone_id"] for item in concatenated}) == 30


def test_filters_are_applied_before_global_sort_and_pagination(tmp_path: Path) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    snapshot_id = store.begin_snapshot(
        universe="allnse", timeframe="DAILY", methodology_version="formation-1.1",
        symbols=None, total_symbols=20,
    )
    rows = []
    for index in range(20):
        zone_type = "DEMAND" if index % 2 == 0 else "SUPPLY"
        quality = float(40 + index)
        confidence = float(100 - index)
        rows.append((
            snapshot_id, f"zone-{index:02d}", f"NSE:S{index:02d}",
            "NSE", f"S{index:02d}",
            "1D", zone_type, "DROP_BASE_RALLY", quality, confidence, "MODERATE",
            "FRESH", 1.0, 100.0, index + 1,
            json.dumps({
                "zone_id": f"zone-{index:02d}",
                "trade_confidence": confidence,
            }),
        ))
    with sqlite3.connect(store.path) as connection:
        connection.executemany(
            """
            INSERT INTO scanner_result_rows(
                snapshot_id, zone_id, instrument_id, exchange, symbol, timeframe,
                zone_type, pattern, zone_quality, trade_confidence,
                trade_confidence_label, lifecycle_status, distance_percent,
                current_price, contextual_rank, row_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows,
        )
        connection.commit()

    total, first_page = store.query_results(
        snapshot_id, zone_type="DEMAND", min_zone_quality=50,
        sort="trade_confidence", descending=True, page=1, page_size=3,
    )
    _, second_page = store.query_results(
        snapshot_id, zone_type="DEMAND", min_zone_quality=50,
        sort="trade_confidence", descending=True, page=2, page_size=3,
    )
    confidences = [
        json.loads(item)["trade_confidence"]
        for item in first_page + second_page
    ]
    assert total == 5
    assert confidences == sorted(confidences, reverse=True)


def test_persisted_query_never_returns_rows_from_another_timeframe(
    tmp_path: Path,
) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    daily_id = store.begin_snapshot(
        universe="nse500",
        timeframe="DAILY",
        methodology_version="formation-1.1",
        symbols=None,
        total_symbols=2,
    )
    weekly_id = store.begin_snapshot(
        universe="nse500",
        timeframe="WEEKLY",
        methodology_version="formation-1.1",
        symbols=None,
        total_symbols=2,
    )
    rows = [
        (
            daily_id,
            "daily-zone",
            "NSE:TCS",
            "NSE",
            "TCS",
            "1D",
            "DEMAND",
            "DROP_BASE_RALLY",
            80.0,
            70.0,
            "MODERATE",
            "FRESH",
            1.0,
            100.0,
            1,
            '{"symbol":"TCS","timeframe":"1D"}',
        ),
        (
            weekly_id,
            "weekly-zone",
            "NSE:TCS",
            "NSE",
            "TCS",
            "1W",
            "DEMAND",
            "DROP_BASE_RALLY",
            80.0,
            70.0,
            "MODERATE",
            "FRESH",
            1.0,
            100.0,
            1,
            '{"symbol":"TCS","timeframe":"1W"}',
        ),
    ]
    with sqlite3.connect(store.path) as connection:
        connection.executemany(
            """
            INSERT INTO scanner_result_rows(
                snapshot_id, zone_id, instrument_id, exchange, symbol,
                timeframe, zone_type, pattern, zone_quality,
                trade_confidence, trade_confidence_label, lifecycle_status,
                distance_percent, current_price, contextual_rank, row_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()

    daily_total, daily_rows = store.query_results(daily_id, timeframe="1D")
    wrong_total, wrong_rows = store.query_results(daily_id, timeframe="1W")
    weekly_total, weekly_rows = store.query_results(weekly_id, timeframe="1W")

    assert daily_total == 1
    assert '"timeframe":"1D"' in daily_rows[0]
    assert (wrong_total, wrong_rows) == (0, [])
    assert weekly_total == 1
    assert '"timeframe":"1W"' in weekly_rows[0]


def test_symbol_checkpoint_is_revision_and_methodology_scoped(tmp_path: Path) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    store.save_symbol_checkpoint(
        instrument_id="NSE:TCS", timeframe="DAILY",
        methodology_version="formation-1.1", market_data_revision="revision-a",
        response=response(zones=2),
    )

    resumed = store.symbol_checkpoint(
        instrument_id="NSE:TCS", timeframe="DAILY",
        methodology_version="formation-1.1", market_data_revision="revision-a",
    )
    changed_candles = store.symbol_checkpoint(
        instrument_id="NSE:TCS", timeframe="DAILY",
        methodology_version="formation-1.1", market_data_revision="revision-b",
    )
    changed_methodology = store.symbol_checkpoint(
        instrument_id="NSE:TCS", timeframe="DAILY",
        methodology_version="formation-1.2", market_data_revision="revision-a",
    )

    assert resumed is not None and resumed.total_zones == 2
    assert changed_candles is None
    assert changed_methodology is None
    assert store.checkpoint_counts("DAILY") == {"COMPLETE": 1}


def test_retryable_checkpoint_does_not_masquerade_as_complete(tmp_path: Path) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    store.fail_symbol_checkpoint(
        instrument_id="NSE:TCS", timeframe="DAILY",
        methodology_version="formation-1.1", market_data_revision="revision-a",
        error="provider timeout",
    )

    assert store.symbol_checkpoint(
        instrument_id="NSE:TCS", timeframe="DAILY",
        methodology_version="formation-1.1", market_data_revision="revision-a",
    ) is None
    assert store.checkpoint_counts("DAILY") == {"RETRYABLE": 1}


def test_worker_lease_allows_one_owner_and_releases_cleanly(tmp_path: Path) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    job_id = store.create_job("nse500", "DAILY", "formation-1.1", 500)

    assert store.claim_job(job_id, "worker-a", lease_seconds=60)
    assert not store.claim_job(job_id, "worker-b", lease_seconds=60)
    assert store.heartbeat_job(job_id, "worker-a", lease_seconds=60)
    store.release_job_lease(job_id, "worker-a")
    assert store.claim_job(job_id, "worker-b", lease_seconds=60)


def test_live_materialization_job_is_reused_across_source_revisions(
    tmp_path: Path,
) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    job_id = store.create_job(
        "allnse", "WEEKLY", "formation-1.1", 2559,
        source_revision="revision-a",
    )
    assert store.claim_job(job_id, "worker-a", lease_seconds=60)

    repeated = store.create_job(
        "allnse", "WEEKLY", "formation-1.1", 2559,
        source_revision="revision-b",
    )

    assert repeated == job_id
    assert not store.update_job(job_id, "RUNNING", owner="worker-b")
    assert store.update_job(job_id, "RUNNING", owner="worker-a")


def test_restart_recovers_expired_job_without_removing_checkpoints(
    tmp_path: Path,
) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    job_id = store.create_job(
        "allnse", "MONTHLY", "formation-1.1", 2390,
        source_revision="daily-adjusted-v1:10y",
    )
    assert store.claim_job(job_id, "dead-worker", lease_seconds=15)
    with store._connection() as connection:
        connection.execute(
            "UPDATE scanner_jobs SET lease_expires_at='2000-01-01T00:00:00+00:00' "
            "WHERE job_id=?",
            (job_id,),
        )
        connection.commit()

    assert store.recover_expired_jobs() == 1
    recovered = next(row for row in store.latest_jobs() if row["job_id"] == job_id)
    assert recovered["status"] == "RETRYABLE"


def test_restart_does_not_recover_a_live_worker_lease(tmp_path: Path) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    job_id = store.create_job(
        "allnse", "WEEKLY", "formation-1.1", 2559,
        source_revision="daily-adjusted-v1",
    )
    assert store.claim_job(job_id, "live-worker", lease_seconds=60)

    assert store.recover_expired_jobs() == 0
    job = next(row for row in store.latest_jobs() if row["job_id"] == job_id)
    assert job["status"] == "RUNNING"


def test_incomplete_snapshot_cannot_be_published(tmp_path: Path) -> None:
    store = PersistentScannerStore(tmp_path / "scanner.sqlite3")
    snapshot_id = store.begin_snapshot(
        universe="allnse", timeframe="DAILY",
        methodology_version="formation-1.1", symbols=None, total_symbols=2390,
    )
    incomplete = response().model_copy(update={
        "universe": "allnse", "total_symbols": 2390,
        "processed_symbols": 176, "failed_symbols": 0,
    })

    try:
        store.publish(snapshot_id, incomplete)
    except ValueError as error:
        assert "Incomplete scanner output" in str(error)
    else:
        raise AssertionError("Incomplete snapshot was published.")


def test_interrupted_resume_merges_exactly_like_uninterrupted_run(
    tmp_path: Path,
) -> None:
    """Operational restart/checkpointing cannot alter canonical payloads."""

    path = tmp_path / "scanner.sqlite3"
    uninterrupted = [
        response(zones=0).model_copy(update={
            "universe": "custom",
            "total_symbols": 1,
            "processed_symbols": 1,
            "canonical_zone_count": index,
            "formation_qualified_count": index,
            "dashboard_qualified_count": index,
        })
        for index in range(1, 5)
    ]
    store = PersistentScannerStore(path)
    for index, item in enumerate(uninterrupted[:2]):
        store.save_symbol_checkpoint(
            instrument_id=f"NSE:TEST{index}", timeframe="DAILY",
            methodology_version="formation-1.1",
            market_data_revision=f"revision-{index}", response=item,
        )

    # Simulate process termination by constructing a new repository instance.
    resumed_store = PersistentScannerStore(path)
    resumed = [
        resumed_store.symbol_checkpoint(
            instrument_id=f"NSE:TEST{index}", timeframe="DAILY",
            methodology_version="formation-1.1",
            market_data_revision=f"revision-{index}",
        )
        for index in range(2)
    ]
    assert all(item is not None for item in resumed)
    for index, item in enumerate(uninterrupted[2:], start=2):
        resumed_store.save_symbol_checkpoint(
            instrument_id=f"NSE:TEST{index}", timeframe="DAILY",
            methodology_version="formation-1.1",
            market_data_revision=f"revision-{index}", response=item,
        )
        resumed.append(item)

    uninterrupted_output = _merge_symbol_responses(
        timeframe="DAILY", universe="custom", expected_symbols=4,
        responses=uninterrupted, failed=0,
    ).model_dump(exclude={"last_completed_at"})
    resumed_output = _merge_symbol_responses(
        timeframe="DAILY", universe="custom", expected_symbols=4,
        responses=[item for item in resumed if item is not None], failed=0,
    ).model_dump(exclude={"last_completed_at"})

    assert resumed_output == uninterrupted_output
    assert resumed_store.checkpoint_counts("DAILY") == {"COMPLETE": 4}
