"""Durable, methodology-versioned storage for completed scanner snapshots.

This module is deliberately an operational wrapper around the frozen scanner.
It stores and retrieves its exact API payload; it never recalculates a zone.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import RLock
from typing import Iterator

from backend.api.models.scanner_response import ZoneResearchResponse


SCANNER_STORAGE_VERSION = "milestone-12.2-resumable"
DERIVED_EOD_STORAGE_VERSION = "milestone-12.3-derived-core-timeframes"
SCANNER_ARCHITECTURE_VERSION = "persistent-all-nse-scanner-v1"


@dataclass(frozen=True)
class StoredSnapshot:
    """One immutable, completely published scanner result."""

    snapshot_id: int
    response: ZoneResearchResponse
    completed_at: str
    stored_at: str


class PersistentScannerStore:
    """SQLite read/write model for scanner snapshots and instrument metadata."""

    def __init__(self, path: Path | None = None) -> None:
        configured = os.getenv("SCANNER_DATABASE_PATH", "").strip()
        self.path = path or (
            Path(configured)
            if configured
            else Path(__file__).resolve().parents[2]
            / "data"
            / "scanner"
            / "alphaedge-scanner.sqlite3"
        )
        self._lock = RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=10000")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        """Create the versioned read model without touching application DB tables."""

        with self._lock, self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS scanner_instruments (
                    instrument_id TEXT PRIMARY KEY,
                    exchange TEXT NOT NULL,
                    exchange_symbol TEXT NOT NULL,
                    display_symbol TEXT NOT NULL,
                    instrument_name TEXT,
                    instrument_type TEXT NOT NULL DEFAULT 'EQUITY',
                    isin TEXT,
                    series TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    provider_identifier TEXT NOT NULL,
                    metadata_updated_at TEXT NOT NULL,
                    UNIQUE(exchange, exchange_symbol)
                );
                CREATE TABLE IF NOT EXISTS scanner_universe_memberships (
                    universe TEXT NOT NULL,
                    instrument_id TEXT NOT NULL,
                    source TEXT,
                    source_updated_at TEXT,
                    PRIMARY KEY(universe, instrument_id),
                    FOREIGN KEY(instrument_id)
                        REFERENCES scanner_instruments(instrument_id)
                );
                CREATE TABLE IF NOT EXISTS scanner_snapshots (
                    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    storage_version TEXT NOT NULL,
                    methodology_version TEXT NOT NULL,
                    universe TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    custom_symbols_key TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL
                        CHECK(status IN ('BUILDING','COMPLETE','FAILED')),
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    stored_at TEXT NOT NULL,
                    total_symbols INTEGER NOT NULL DEFAULT 0,
                    successful_instruments INTEGER NOT NULL DEFAULT 0,
                    failed_instruments INTEGER NOT NULL DEFAULT 0,
                    result_count INTEGER NOT NULL DEFAULT 0,
                    payload_json TEXT,
                    error_message TEXT
                );
                CREATE INDEX IF NOT EXISTS ix_scanner_snapshot_lookup
                    ON scanner_snapshots(
                        universe, timeframe, custom_symbols_key,
                        methodology_version, status, snapshot_id DESC
                    );
                CREATE INDEX IF NOT EXISTS ix_scanner_snapshot_completed
                    ON scanner_snapshots(completed_at DESC) WHERE status='COMPLETE';
                CREATE INDEX IF NOT EXISTS ix_scanner_membership_universe
                    ON scanner_universe_memberships(universe, instrument_id);
                CREATE TABLE IF NOT EXISTS scanner_result_rows (
                    snapshot_id INTEGER NOT NULL,
                    zone_id TEXT NOT NULL,
                    instrument_id TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    zone_type TEXT NOT NULL,
                    pattern TEXT,
                    zone_quality REAL NOT NULL,
                    trade_confidence REAL,
                    trade_confidence_label TEXT,
                    lifecycle_status TEXT,
                    distance_percent REAL NOT NULL,
                    current_price REAL NOT NULL,
                    contextual_rank INTEGER NOT NULL,
                    row_json TEXT NOT NULL,
                    PRIMARY KEY(snapshot_id, zone_id),
                    FOREIGN KEY(snapshot_id) REFERENCES scanner_snapshots(snapshot_id)
                );
                CREATE INDEX IF NOT EXISTS ix_scanner_results_filter
                    ON scanner_result_rows(
                        snapshot_id, zone_type, pattern, zone_quality,
                        trade_confidence, lifecycle_status, distance_percent
                    );
                CREATE INDEX IF NOT EXISTS ix_scanner_results_symbol
                    ON scanner_result_rows(snapshot_id, symbol);
                CREATE TABLE IF NOT EXISTS scanner_jobs (
                    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    universe TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    methodology_version TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN (
                        'QUEUED','RUNNING','COMPLETE','FAILED','RETRYABLE'
                    )),
                    total_instruments INTEGER NOT NULL,
                    processed_instruments INTEGER NOT NULL DEFAULT 0,
                    failed_instruments INTEGER NOT NULL DEFAULT 0,
                    queued_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT
                );
                CREATE INDEX IF NOT EXISTS ix_scanner_jobs_status
                    ON scanner_jobs(status, job_id DESC);
                CREATE TABLE IF NOT EXISTS scanner_timeframe_materializations (
                    universe TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    methodology_version TEXT NOT NULL,
                    state TEXT NOT NULL CHECK(state IN (
                        'READY','BUILDING','STALE','FAILED','UNAVAILABLE'
                    )),
                    snapshot_id INTEGER,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(universe, timeframe, methodology_version)
                );
                CREATE TABLE IF NOT EXISTS scanner_symbol_checkpoints (
                    instrument_id TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    methodology_version TEXT NOT NULL,
                    market_data_revision TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN (
                        'COMPLETE','FAILED','RETRYABLE'
                    )),
                    response_json TEXT,
                    error_message TEXT,
                    completed_at TEXT NOT NULL,
                    PRIMARY KEY(
                        instrument_id, timeframe, methodology_version,
                        market_data_revision
                    )
                );
                CREATE INDEX IF NOT EXISTS ix_scanner_symbol_checkpoint_resume
                    ON scanner_symbol_checkpoints(
                        timeframe, methodology_version, status, instrument_id
                    );
                """
            )
            job_columns = {
                str(row[1])
                for row in connection.execute("PRAGMA table_info(scanner_jobs)")
            }
            for column, declaration in (
                ("lease_owner", "TEXT"),
                ("lease_expires_at", "TEXT"),
                ("heartbeat_at", "TEXT"),
                ("source_revision", "TEXT NOT NULL DEFAULT ''"),
            ):
                if column not in job_columns:
                    connection.execute(
                        f"ALTER TABLE scanner_jobs ADD COLUMN {column} {declaration}"
                    )
            connection.commit()
            connection.execute(
                """
                UPDATE scanner_timeframe_materializations
                SET state='READY', updated_at=?
                WHERE snapshot_id IN (
                    SELECT snapshot_id FROM scanner_snapshots
                    WHERE storage_version=? AND status='COMPLETE'
                )
                """,
                (datetime.now(UTC).isoformat(), SCANNER_STORAGE_VERSION),
            )
            connection.commit()

    def recover_expired_jobs(self) -> int:
        """Recover RUNNING rows left by the previous single backend process."""

        now = datetime.now(UTC).isoformat()
        with self._lock, self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE scanner_jobs
                SET status='RETRYABLE', completed_at=?, lease_owner=NULL,
                    lease_expires_at=NULL,
                    error_message=COALESCE(
                        error_message, 'Recovered after worker restart.'
                    )
                WHERE status='RUNNING'
                  AND (lease_expires_at IS NULL OR lease_expires_at<?)
                """,
                (now, now),
            )
            connection.commit()
            return int(cursor.rowcount)

    def symbol_checkpoint(
        self,
        *,
        instrument_id: str,
        timeframe: str,
        methodology_version: str,
        market_data_revision: str,
    ) -> ZoneResearchResponse | None:
        """Load one completed canonical symbol result, rejecting stale revisions."""

        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT response_json FROM scanner_symbol_checkpoints
                WHERE instrument_id=? AND timeframe=? AND methodology_version=?
                  AND market_data_revision=? AND status='COMPLETE'
                """,
                (
                    instrument_id, timeframe, methodology_version,
                    market_data_revision,
                ),
            ).fetchone()
        if row is None or not row["response_json"]:
            return None
        try:
            return ZoneResearchResponse.model_validate_json(row["response_json"])
        except Exception:
            return None

    def save_symbol_checkpoint(
        self,
        *,
        instrument_id: str,
        timeframe: str,
        methodology_version: str,
        market_data_revision: str,
        response: ZoneResearchResponse,
    ) -> None:
        """Atomically persist a completed per-symbol canonical result."""

        with self._lock, self._connection() as connection:
            connection.execute(
                """
                INSERT INTO scanner_symbol_checkpoints(
                    instrument_id, timeframe, methodology_version,
                    market_data_revision, status, response_json, completed_at
                ) VALUES (?, ?, ?, ?, 'COMPLETE', ?, ?)
                ON CONFLICT(
                    instrument_id, timeframe, methodology_version,
                    market_data_revision
                ) DO UPDATE SET
                    status='COMPLETE', response_json=excluded.response_json,
                    error_message=NULL, completed_at=excluded.completed_at
                """,
                (
                    instrument_id, timeframe, methodology_version,
                    market_data_revision, response.model_dump_json(),
                    datetime.now(UTC).isoformat(),
                ),
            )
            connection.commit()

    def fail_symbol_checkpoint(
        self,
        *,
        instrument_id: str,
        timeframe: str,
        methodology_version: str,
        market_data_revision: str,
        error: str,
        retryable: bool = True,
    ) -> None:
        with self._lock, self._connection() as connection:
            connection.execute(
                """
                INSERT INTO scanner_symbol_checkpoints(
                    instrument_id, timeframe, methodology_version,
                    market_data_revision, status, error_message, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(
                    instrument_id, timeframe, methodology_version,
                    market_data_revision
                ) DO UPDATE SET status=excluded.status,
                    response_json=NULL, error_message=excluded.error_message,
                    completed_at=excluded.completed_at
                """,
                (
                    instrument_id, timeframe, methodology_version,
                    market_data_revision,
                    "RETRYABLE" if retryable else "FAILED", error[:2000],
                    datetime.now(UTC).isoformat(),
                ),
            )
            connection.commit()

    def checkpoint_counts(self, timeframe: str) -> dict[str, int]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT status, COUNT(*) count FROM scanner_symbol_checkpoints
                WHERE timeframe=? AND methodology_version=? GROUP BY status
                """,
                (timeframe, self._active_methodology_version()),
            ).fetchall()
        return {str(row["status"]): int(row["count"]) for row in rows}

    @staticmethod
    def symbols_key(symbols: list[str] | None) -> str:
        return ",".join(sorted({item.strip().upper() for item in symbols or []}))

    def seed_universe(
        self,
        universe: str,
        symbols: list[str],
        *,
        source: str | None = None,
        source_updated_at: str | None = None,
    ) -> None:
        """Persist stable NSE identities while preserving exchange identity."""

        now = datetime.now(UTC).isoformat()
        with self._lock, self._connection() as connection:
            for symbol in symbols:
                instrument_id = f"NSE:{symbol}"
                connection.execute(
                    """
                    INSERT INTO scanner_instruments(
                        instrument_id, exchange, exchange_symbol, display_symbol,
                        provider_identifier, metadata_updated_at
                    ) VALUES (?, 'NSE', ?, ?, ?, ?)
                    ON CONFLICT(instrument_id) DO UPDATE SET
                        display_symbol=excluded.display_symbol,
                        provider_identifier=excluded.provider_identifier,
                        metadata_updated_at=excluded.metadata_updated_at
                    """,
                    (instrument_id, symbol, symbol, f"{symbol}.NS", now),
                )
                connection.execute(
                    """
                    INSERT INTO scanner_universe_memberships(
                        universe, instrument_id, source, source_updated_at
                    ) VALUES (?, ?, ?, ?)
                    ON CONFLICT(universe, instrument_id) DO UPDATE SET
                        source=excluded.source,
                        source_updated_at=excluded.source_updated_at
                    """,
                    (universe, instrument_id, source, source_updated_at),
                )
            connection.commit()

    def begin_snapshot(
        self,
        *,
        universe: str,
        timeframe: str,
        methodology_version: str,
        symbols: list[str] | None,
        total_symbols: int,
        storage_version: str = SCANNER_STORAGE_VERSION,
    ) -> int:
        now = datetime.now(UTC).isoformat()
        with self._lock, self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO scanner_snapshots(
                    storage_version, methodology_version, universe, timeframe,
                    custom_symbols_key, status, started_at, stored_at, total_symbols
                ) VALUES (?, ?, ?, ?, ?, 'BUILDING', ?, ?, ?)
                """,
                (
                    storage_version,
                    methodology_version,
                    universe,
                    timeframe,
                    self.symbols_key(symbols),
                    now,
                    now,
                    total_symbols,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def publish(self, snapshot_id: int, response: ZoneResearchResponse) -> None:
        """Atomically make a fully calculated response the new current snapshot."""

        if (
            response.processed_symbols + response.failed_symbols
            != response.total_symbols
        ):
            raise ValueError(
                "Incomplete scanner output cannot be published as COMPLETE."
            )
        now = datetime.now(UTC).isoformat()
        payload = response.model_dump_json()
        with self._lock, self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                UPDATE scanner_snapshots SET
                    status='COMPLETE', completed_at=?, stored_at=?,
                    successful_instruments=?, failed_instruments=?, result_count=?,
                    payload_json=?, error_message=NULL
                WHERE snapshot_id=? AND status='BUILDING'
                """,
                (
                    response.last_completed_at or now,
                    now,
                    response.processed_symbols,
                    response.failed_symbols,
                    response.total_zones,
                    payload,
                    snapshot_id,
                ),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                raise ValueError("Scanner snapshot cannot be published from its state.")
            connection.execute(
                "DELETE FROM scanner_result_rows WHERE snapshot_id=?",
                (snapshot_id,),
            )
            for rank, item in enumerate(response.results, start=1):
                confidence = item.trade_confidence
                zone_id = item.zone_id or (
                    f"{item.symbol}:{item.timeframe}:{item.zone_type}:"
                    f"{item.base_index}:{item.proximal_price}:{item.distal_price}"
                )
                connection.execute(
                    """
                    INSERT INTO scanner_result_rows(
                        snapshot_id, zone_id, instrument_id, exchange, symbol,
                        timeframe, zone_type, pattern, zone_quality,
                        trade_confidence, trade_confidence_label,
                        lifecycle_status, distance_percent, current_price,
                        contextual_rank, row_json
                    ) VALUES (?, ?, ?, 'NSE', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_id,
                        zone_id,
                        f"NSE:{item.symbol}",
                        item.symbol,
                        item.timeframe,
                        item.zone_type,
                        item.pattern_type,
                        item.zone_score,
                        confidence.score if confidence else None,
                        confidence.label if confidence else None,
                        item.lifecycle_status,
                        item.distance_percent,
                        item.current_price,
                        rank,
                        item.model_dump_json(),
                    ),
                )
            connection.execute(
                """
                INSERT INTO scanner_timeframe_materializations(
                    universe, timeframe, methodology_version, state,
                    snapshot_id, updated_at
                ) SELECT universe, timeframe, methodology_version, 'READY', ?, ?
                  FROM scanner_snapshots WHERE snapshot_id=?
                ON CONFLICT(universe, timeframe, methodology_version) DO UPDATE SET
                    state='READY', snapshot_id=excluded.snapshot_id,
                    updated_at=excluded.updated_at
                """,
                (snapshot_id, now, snapshot_id),
            )
            connection.commit()

    def fail(self, snapshot_id: int, error: str) -> None:
        with self._lock, self._connection() as connection:
            connection.execute(
                """
                UPDATE scanner_snapshots SET status='FAILED', error_message=?
                WHERE snapshot_id=? AND status='BUILDING'
                """,
                (error[:2000], snapshot_id),
            )
            connection.execute(
                """
                UPDATE scanner_timeframe_materializations
                SET state='FAILED', updated_at=?
                WHERE (universe, timeframe, methodology_version) = (
                    SELECT universe, timeframe, methodology_version
                    FROM scanner_snapshots WHERE snapshot_id=?
                )
                """,
                (datetime.now(UTC).isoformat(), snapshot_id),
            )
            connection.commit()

    def latest_complete(
        self,
        *,
        universe: str,
        timeframe: str,
        methodology_version: str,
        symbols: list[str] | None,
        storage_version: str = SCANNER_STORAGE_VERSION,
    ) -> StoredSnapshot | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT snapshot_id, payload_json, completed_at, stored_at
                FROM scanner_snapshots
                WHERE universe=? AND timeframe=? AND custom_symbols_key=?
                  AND methodology_version=? AND storage_version=? AND status='COMPLETE'
                  AND successful_instruments + failed_instruments=total_symbols
                ORDER BY snapshot_id DESC LIMIT 1
                """,
                (
                    universe,
                    timeframe,
                    self.symbols_key(symbols),
                    methodology_version,
                    storage_version,
                ),
            ).fetchone()
        if row is None or not row["payload_json"]:
            return None
        return StoredSnapshot(
            snapshot_id=int(row["snapshot_id"]),
            response=ZoneResearchResponse.model_validate_json(row["payload_json"]),
            completed_at=str(row["completed_at"]),
            stored_at=str(row["stored_at"]),
        )

    def status_counts(self) -> dict[str, int]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT status, COUNT(*) count FROM scanner_snapshots GROUP BY status"
            ).fetchall()
        return {str(row["status"]): int(row["count"]) for row in rows}

    def latest_jobs(self, limit: int = 20) -> list[dict[str, object]]:
        """Return durable operational progress without starting scanner work."""

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT job_id, universe, timeframe, methodology_version, status,
                       source_revision,
                       total_instruments, processed_instruments,
                       failed_instruments, queued_at, started_at, completed_at,
                       error_message
                FROM scanner_jobs ORDER BY job_id DESC LIMIT ?
                """,
                (max(1, min(100, limit)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def materialization_progress(
        self, universe: str, timeframe: str
    ) -> dict[str, object] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT status, total_instruments, processed_instruments,
                       failed_instruments
                FROM scanner_jobs
                WHERE universe=? AND timeframe=? AND methodology_version=?
                ORDER BY job_id DESC LIMIT 1
                """,
                (universe, timeframe, self._active_methodology_version()),
            ).fetchone()
        return dict(row) if row else None

    def instrument_counts(self) -> dict[str, int]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT universe, COUNT(*) count
                FROM scanner_universe_memberships GROUP BY universe
                """
            ).fetchall()
        return {str(row["universe"]): int(row["count"]) for row in rows}

    def materialization_states(self, universe: str) -> dict[str, str]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT timeframe, state FROM scanner_timeframe_materializations
                WHERE universe=? AND methodology_version=?
                """,
                (universe, self._active_methodology_version()),
            ).fetchall()
        return {str(row["timeframe"]): str(row["state"]) for row in rows}

    def mark_materializations_stale(
        self, universe: str, timeframes: tuple[str, ...]
    ) -> None:
        if not timeframes:
            return
        placeholders = ",".join("?" for _ in timeframes)
        with self._lock, self._connection() as connection:
            connection.execute(
                f"""
                UPDATE scanner_timeframe_materializations
                SET state='STALE', updated_at=?
                WHERE universe=? AND methodology_version=?
                  AND timeframe IN ({placeholders})
                """,
                (
                    datetime.now(UTC).isoformat(), universe,
                    self._active_methodology_version(), *timeframes,
                ),
            )
            connection.commit()

    @staticmethod
    def _active_methodology_version() -> str:
        # Local import avoids making the storage schema depend on engine modules.
        from backend.config.canonical_methodology import (
            SCANNER_METHODOLOGY_CACHE_VERSION,
        )

        return SCANNER_METHODOLOGY_CACHE_VERSION

    def create_job(
        self,
        universe: str,
        timeframe: str,
        methodology_version: str,
        total_instruments: int,
        source_revision: str = "",
    ) -> int:
        now = datetime.now(UTC).isoformat()
        with self._lock, self._connection() as connection:
            active = connection.execute(
                """
                SELECT job_id FROM scanner_jobs
                WHERE universe=? AND timeframe=? AND methodology_version=?
                  AND (
                    status='QUEUED'
                    OR (status='RUNNING' AND lease_expires_at>?)
                  )
                ORDER BY job_id DESC LIMIT 1
                """,
                (universe, timeframe, methodology_version, now),
            ).fetchone()
            if active is not None:
                return int(active["job_id"])
            # Creating a replacement for the same materialization is the safe
            # recovery boundary. Read-only processes must never mutate a live
            # worker merely because they opened the shared database.
            connection.execute(
                """
                UPDATE scanner_jobs
                SET status='RETRYABLE', completed_at=?,
                    error_message=COALESCE(
                        error_message,
                        'Superseded by a replacement refresh after interruption.'
                    )
                WHERE universe=? AND timeframe=? AND methodology_version=?
                  AND status IN ('QUEUED', 'RUNNING')
                """,
                (now, universe, timeframe, methodology_version),
            )
            connection.execute(
                """
                UPDATE scanner_snapshots
                SET status='FAILED', error_message=COALESCE(
                    error_message,
                    'Superseded by a replacement refresh after interruption.'
                )
                WHERE universe=? AND timeframe=? AND methodology_version=?
                  AND status='BUILDING'
                """,
                (universe, timeframe, methodology_version),
            )
            cursor = connection.execute(
                """
                INSERT INTO scanner_jobs(
                    universe, timeframe, methodology_version, status,
                    total_instruments, queued_at, source_revision
                ) VALUES (?, ?, ?, 'QUEUED', ?, ?, ?)
                """,
                (
                    universe, timeframe, methodology_version,
                    total_instruments, now, source_revision,
                ),
            )
            connection.execute(
                """
                INSERT INTO scanner_timeframe_materializations(
                    universe, timeframe, methodology_version, state, updated_at
                ) VALUES (?, ?, ?, 'BUILDING', ?)
                ON CONFLICT(universe, timeframe, methodology_version) DO UPDATE SET
                    state='BUILDING', updated_at=excluded.updated_at
                """,
                (universe, timeframe, methodology_version, now),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def update_job(
        self,
        job_id: int,
        status: str,
        *,
        processed: int | None = None,
        failed: int | None = None,
        error: str | None = None,
        owner: str | None = None,
    ) -> bool:
        now = datetime.now(UTC).isoformat()
        assignments = ["status=?"]
        values: list[object] = [status]
        if status == "RUNNING":
            assignments.append("started_at=COALESCE(started_at, ?)")
            values.append(now)
        if status in {"COMPLETE", "FAILED", "RETRYABLE"}:
            assignments.append("completed_at=?")
            values.append(now)
        if processed is not None:
            assignments.append("processed_instruments=?")
            values.append(processed)
        if failed is not None:
            assignments.append("failed_instruments=?")
            values.append(failed)
        if error is not None:
            assignments.append("error_message=?")
            values.append(error[:2000])
        values.append(job_id)
        owner_clause = ""
        if owner is not None:
            owner_clause = " AND lease_owner=?"
            values.append(owner)
        with self._lock, self._connection() as connection:
            cursor = connection.execute(
                f"UPDATE scanner_jobs SET {', '.join(assignments)} "
                f"WHERE job_id=?{owner_clause}",
                values,
            )
            connection.commit()
        return cursor.rowcount == 1

    def claim_job(self, job_id: int, owner: str, lease_seconds: int = 90) -> bool:
        """Acquire a cross-process lease, recovering only an expired owner."""

        now = datetime.now(UTC)
        expires = now + timedelta(seconds=max(15, lease_seconds))
        with self._lock, self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE scanner_jobs SET lease_owner=?, lease_expires_at=?,
                    heartbeat_at=?, status='RUNNING',
                    started_at=COALESCE(started_at, ?)
                WHERE job_id=? AND status IN ('QUEUED','RUNNING','RETRYABLE')
                  AND (
                    lease_owner IS NULL OR lease_owner=? OR lease_expires_at IS NULL
                    OR lease_expires_at<?
                  )
                """,
                (
                    owner, expires.isoformat(), now.isoformat(), now.isoformat(),
                    job_id, owner, now.isoformat(),
                ),
            )
            connection.commit()
            return cursor.rowcount == 1

    def heartbeat_job(self, job_id: int, owner: str, lease_seconds: int = 90) -> bool:
        now = datetime.now(UTC)
        with self._lock, self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE scanner_jobs SET heartbeat_at=?, lease_expires_at=?
                WHERE job_id=? AND status='RUNNING' AND lease_owner=?
                """,
                (
                    now.isoformat(),
                    (now + timedelta(seconds=max(15, lease_seconds))).isoformat(),
                    job_id, owner,
                ),
            )
            connection.commit()
            return cursor.rowcount == 1

    def release_job_lease(self, job_id: int, owner: str) -> None:
        with self._lock, self._connection() as connection:
            connection.execute(
                """
                UPDATE scanner_jobs SET lease_owner=NULL, lease_expires_at=NULL
                WHERE job_id=? AND lease_owner=?
                """,
                (job_id, owner),
            )
            connection.commit()

    def query_results(
        self,
        snapshot_id: int,
        *,
        timeframe: str | None = None,
        zone_type: str | None = None,
        pattern: str | None = None,
        min_zone_quality: float | None = None,
        min_trade_confidence: float | None = None,
        lifecycle: str | None = None,
        status: str | None = None,
        symbol: str | None = None,
        max_distance: float | None = None,
        sort: str = "contextual_rank",
        descending: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[int, list[str]]:
        columns = {
            "contextual_rank": "contextual_rank",
            "zone_quality": "zone_quality",
            "trade_confidence": "trade_confidence",
            "distance": "distance_percent",
            "symbol": "symbol",
        }
        if sort not in columns:
            raise ValueError(f"Unsupported scanner sort: {sort}")
        conditions = ["snapshot_id=?"]
        values: list[object] = [snapshot_id]
        if timeframe:
            conditions.append("timeframe=?")
            values.append(timeframe)
        for column, value in (
            ("zone_type", zone_type),
            ("pattern", pattern),
            ("lifecycle_status", lifecycle),
        ):
            if value:
                conditions.append(f"{column}=?")
                values.append(value)
        if symbol:
            conditions.append("symbol LIKE ?")
            values.append(f"%{symbol.strip().upper()}%")
        if status:
            conditions.append("json_extract(row_json, '$.status')=?")
            values.append(status)
        if min_zone_quality is not None:
            conditions.append("zone_quality>=?")
            values.append(min_zone_quality)
        if min_trade_confidence is not None:
            conditions.append("trade_confidence>=?")
            values.append(min_trade_confidence)
        if max_distance is not None:
            conditions.append("distance_percent<=?")
            values.append(max_distance)
        where = " AND ".join(conditions)
        order = "DESC" if descending else "ASC"
        offset = (max(1, page) - 1) * max(1, page_size)
        with self._connection() as connection:
            total = int(
                connection.execute(
                    f"SELECT COUNT(*) FROM scanner_result_rows WHERE {where}",
                    values,
                ).fetchone()[0]
            )
            rows = connection.execute(
                f"""
                SELECT row_json FROM scanner_result_rows WHERE {where}
                ORDER BY {columns[sort]} {order}, contextual_rank ASC, zone_id ASC
                LIMIT ? OFFSET ?
                """,
                (*values, min(500, max(1, page_size)), offset),
            ).fetchall()
        return total, [str(row["row_json"]) for row in rows]
