# flake8: noqa: E501
"""Provider-isolated persistence for Dhan shadow candles and checkpoints."""

from __future__ import annotations

import sqlite3
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Iterator

import pandas as pd
from pandas import DataFrame

from backend.data_providers.dhan import DhanInstrument


@dataclass(frozen=True)
class ShadowMergeResult:
    inserted: int = 0
    corrected: int = 0
    unchanged: int = 0
    rejected: int = 0


class DhanShadowStore:
    """Separate database guarantees Dhan can never overwrite Yahoo production data."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("backend/data/shadow/dhan-shadow.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self.initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=30000")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS dhan_instruments (
                    instrument_id TEXT PRIMARY KEY, exchange TEXT NOT NULL,
                    security_id TEXT NOT NULL, symbol TEXT NOT NULL, isin TEXT NOT NULL,
                    series TEXT NOT NULL, category TEXT NOT NULL, display_name TEXT,
                    provider_addressable INTEGER NOT NULL DEFAULT 1,
                    synchronized_at TEXT NOT NULL,
                    UNIQUE(exchange, security_id)
                );
                CREATE INDEX IF NOT EXISTS ix_dhan_instruments_category ON dhan_instruments(category, symbol);
                CREATE INDEX IF NOT EXISTS ix_dhan_instruments_isin ON dhan_instruments(isin, exchange);
                CREATE TABLE IF NOT EXISTS dhan_shadow_candles (
                    instrument_id TEXT NOT NULL, timeframe TEXT NOT NULL,
                    source_interval TEXT NOT NULL, timestamp TEXT NOT NULL,
                    open REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL,
                    close REAL NOT NULL, volume REAL, quality_state TEXT NOT NULL,
                    provider TEXT NOT NULL DEFAULT 'dhan', adjustment_semantics TEXT NOT NULL,
                    candle_revision TEXT NOT NULL DEFAULT 'raw-v1', retrieved_at TEXT NOT NULL,
                    PRIMARY KEY(instrument_id, timeframe, timestamp),
                    FOREIGN KEY(instrument_id) REFERENCES dhan_instruments(instrument_id)
                );
                CREATE INDEX IF NOT EXISTS ix_dhan_shadow_candles_read
                    ON dhan_shadow_candles(instrument_id, timeframe, timestamp);
                CREATE TABLE IF NOT EXISTS dhan_shadow_checkpoints (
                    cohort TEXT NOT NULL, instrument_id TEXT NOT NULL,
                    timeframe TEXT NOT NULL, source_semantics TEXT NOT NULL,
                    status TEXT NOT NULL, candle_count INTEGER NOT NULL DEFAULT 0,
                    first_timestamp TEXT, last_timestamp TEXT, attempts INTEGER NOT NULL DEFAULT 1,
                    error_code TEXT, updated_at TEXT NOT NULL,
                    PRIMARY KEY(cohort, instrument_id, timeframe, source_semantics)
                );
                CREATE TABLE IF NOT EXISTS dhan_shadow_data_quality_conflicts (
                    instrument_id TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    evidence TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    PRIMARY KEY(instrument_id, timeframe, timestamp)
                );
                CREATE INDEX IF NOT EXISTS ix_dhan_quality_conflicts
                    ON dhan_shadow_data_quality_conflicts(instrument_id, timeframe);
                CREATE TABLE IF NOT EXISTS dhan_shadow_zones (
                    cohort TEXT NOT NULL, instrument_id TEXT NOT NULL, timeframe TEXT NOT NULL,
                    zone_identity TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL,
                    PRIMARY KEY(cohort, instrument_id, timeframe, zone_identity)
                );
                CREATE TABLE IF NOT EXISTS dhan_materialization_snapshots (
                    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT, cohort TEXT NOT NULL,
                    timeframe TEXT NOT NULL, provider TEXT NOT NULL, status TEXT NOT NULL,
                    total_instruments INTEGER NOT NULL, processed_instruments INTEGER NOT NULL DEFAULT 0,
                    zone_count INTEGER NOT NULL DEFAULT 0, qualified_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL, completed_at TEXT, source_fingerprint TEXT,
                    methodology_version TEXT
                );
                CREATE INDEX IF NOT EXISTS ix_dhan_materialization_ready
                    ON dhan_materialization_snapshots(provider, cohort, timeframe, status, snapshot_id DESC);
                CREATE TABLE IF NOT EXISTS dhan_canonical_checkpoints (
                    cohort TEXT NOT NULL, instrument_id TEXT NOT NULL, timeframe TEXT NOT NULL,
                    status TEXT NOT NULL, zone_count INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL, error_code TEXT,
                    PRIMARY KEY(cohort,instrument_id,timeframe)
                );
                CREATE TABLE IF NOT EXISTS dhan_canonical_terminal_exclusions (
                    cohort TEXT NOT NULL, instrument_id TEXT NOT NULL, timeframe TEXT NOT NULL,
                    status TEXT NOT NULL, reason_code TEXT NOT NULL, updated_at TEXT NOT NULL,
                    PRIMARY KEY(cohort,instrument_id,timeframe)
                );
                CREATE TABLE IF NOT EXISTS dhan_structured_rebuild_checkpoints (
                    cohort TEXT NOT NULL, instrument_id TEXT NOT NULL, timeframe TEXT NOT NULL,
                    persistence_version TEXT NOT NULL, status TEXT NOT NULL, updated_at TEXT NOT NULL,
                    PRIMARY KEY(cohort,instrument_id,timeframe,persistence_version)
                );
                CREATE TABLE IF NOT EXISTS dhan_active_zone_exclusions (
                    cohort TEXT NOT NULL, instrument_id TEXT NOT NULL, timeframe TEXT NOT NULL,
                    reason_code TEXT NOT NULL, excluded_at TEXT NOT NULL,
                    PRIMARY KEY(cohort,instrument_id,timeframe)
                );
                CREATE TABLE IF NOT EXISTS dhan_dashboard_result_snapshots (
                    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cohort TEXT NOT NULL, timeframe TEXT NOT NULL,
                    provider TEXT NOT NULL DEFAULT 'dhan', status TEXT NOT NULL,
                    total_instruments INTEGER NOT NULL, processed_instruments INTEGER NOT NULL DEFAULT 0,
                    result_count INTEGER NOT NULL DEFAULT 0, exclusion_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL, completed_at TEXT, error TEXT,
                    methodology_version TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_dhan_dashboard_ready
                    ON dhan_dashboard_result_snapshots(provider,cohort,timeframe,status,snapshot_id DESC);
                CREATE TABLE IF NOT EXISTS dhan_dashboard_result_rows (
                    snapshot_id INTEGER NOT NULL, row_id TEXT NOT NULL,
                    instrument_id TEXT NOT NULL, symbol TEXT NOT NULL, exchange TEXT NOT NULL,
                    zone_type TEXT NOT NULL, pattern_type TEXT, zone_quality REAL NOT NULL,
                    trade_confidence REAL, distance_percent REAL NOT NULL,
                    dashboard_qualified INTEGER NOT NULL, payload TEXT NOT NULL,
                    PRIMARY KEY(snapshot_id,row_id),
                    FOREIGN KEY(snapshot_id) REFERENCES dhan_dashboard_result_snapshots(snapshot_id)
                );
                CREATE INDEX IF NOT EXISTS ix_dhan_dashboard_result_query
                    ON dhan_dashboard_result_rows(snapshot_id,dashboard_qualified,zone_type,trade_confidence,zone_quality,distance_percent,symbol,row_id);
                CREATE TABLE IF NOT EXISTS dhan_dashboard_result_checkpoints (
                    snapshot_id INTEGER NOT NULL, instrument_id TEXT NOT NULL,
                    status TEXT NOT NULL, error_code TEXT, updated_at TEXT NOT NULL,
                    PRIMARY KEY(snapshot_id,instrument_id),
                    FOREIGN KEY(snapshot_id) REFERENCES dhan_dashboard_result_snapshots(snapshot_id)
                );
                CREATE TABLE IF NOT EXISTS dhan_incremental_update_runs (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL DEFAULT 'READY',
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    latest_trading_date TEXT,
                    instruments_checked INTEGER NOT NULL DEFAULT 0,
                    instruments_changed INTEGER NOT NULL DEFAULT 0,
                    instruments_failed INTEGER NOT NULL DEFAULT 0,
                    progress_completed INTEGER NOT NULL DEFAULT 0,
                    progress_total INTEGER NOT NULL DEFAULT 0,
                    affected_timeframes TEXT NOT NULL DEFAULT '',
                    cancellation_requested_at TEXT,
                    error TEXT
                );
                CREATE INDEX IF NOT EXISTS ix_dhan_incremental_update_runs_status
                    ON dhan_incremental_update_runs(status, run_id DESC);
                CREATE TABLE IF NOT EXISTS dhan_incremental_dirty_instruments (
                    instrument_id TEXT NOT NULL, timeframe TEXT NOT NULL,
                    reason_code TEXT NOT NULL, updated_at TEXT NOT NULL,
                    earliest_changed_timestamp TEXT,
                    PRIMARY KEY(instrument_id,timeframe)
                );
                CREATE TABLE IF NOT EXISTS dhan_incremental_pathological_instruments (
                    run_id INTEGER NOT NULL,
                    instrument_id TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    candle_count INTEGER NOT NULL,
                    zone_count INTEGER NOT NULL,
                    stage TEXT NOT NULL,
                    elapsed_seconds REAL NOT NULL,
                    attempt INTEGER NOT NULL,
                    result TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    PRIMARY KEY(run_id,instrument_id,timeframe,attempt)
                );
                """)
            columns = {
                str(row[1])
                for row in connection.execute(
                    "PRAGMA table_info(dhan_incremental_update_runs)"
                ).fetchall()
            }
            if "stage" not in columns:
                connection.execute(
                    "ALTER TABLE dhan_incremental_update_runs "
                    "ADD COLUMN stage TEXT NOT NULL DEFAULT 'READY'"
                )
            if "cancellation_requested_at" not in columns:
                connection.execute(
                    "ALTER TABLE dhan_incremental_update_runs "
                    "ADD COLUMN cancellation_requested_at TEXT"
                )
            if "progress_completed" not in columns:
                connection.execute(
                    "ALTER TABLE dhan_incremental_update_runs "
                    "ADD COLUMN progress_completed INTEGER NOT NULL DEFAULT 0"
                )
            if "progress_total" not in columns:
                connection.execute(
                    "ALTER TABLE dhan_incremental_update_runs "
                    "ADD COLUMN progress_total INTEGER NOT NULL DEFAULT 0"
                )
            if "affected_timeframes" not in columns:
                connection.execute(
                    "ALTER TABLE dhan_incremental_update_runs "
                    "ADD COLUMN affected_timeframes TEXT NOT NULL DEFAULT ''"
                )
            dirty_columns = {
                str(row[1])
                for row in connection.execute(
                    "PRAGMA table_info(dhan_incremental_dirty_instruments)"
                ).fetchall()
            }
            if "earliest_changed_timestamp" not in dirty_columns:
                connection.execute(
                    "ALTER TABLE dhan_incremental_dirty_instruments "
                    "ADD COLUMN earliest_changed_timestamp TEXT"
                )
            connection.commit()

    def begin_materialization(self, cohort: str, timeframe: str, total: int, *, methodology_version: str = "formation-1.1") -> int:
        with self.connection() as connection:
            cur = connection.execute("INSERT INTO dhan_materialization_snapshots(cohort,timeframe,provider,status,total_instruments,created_at,methodology_version) VALUES (?,?,?,?,?,?,?)", (cohort,timeframe,"dhan","BUILDING",total,datetime.now(UTC).isoformat(),methodology_version))
            connection.commit()
            return int(cur.lastrowid)

    def canonical_complete(self, cohort: str, instrument_id: str, timeframe: str) -> bool:
        with self.connection() as connection:
            return connection.execute("SELECT 1 FROM dhan_canonical_checkpoints WHERE cohort=? AND instrument_id=? AND timeframe=? AND status='COMPLETE'", (cohort,instrument_id,timeframe)).fetchone() is not None

    def exclude_canonical(self, cohort: str, instrument_id: str, timeframe: str, status: str, reason_code: str) -> None:
        if status not in {"NO_DATA", "QUARANTINED", "FAILED_PERMANENT"}:
            raise ValueError("Canonical exclusion must be terminal.")
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO dhan_canonical_terminal_exclusions VALUES (?,?,?,?,?,?) ON CONFLICT(cohort,instrument_id,timeframe) DO UPDATE SET status=excluded.status,reason_code=excluded.reason_code,updated_at=excluded.updated_at",
                (cohort, instrument_id, timeframe, status, reason_code, datetime.now(UTC).isoformat()),
            )
            connection.commit()

    def structured_rebuild_complete(self, cohort: str, instrument_id: str, timeframe: str, version: str) -> bool:
        with self.connection() as connection:
            return connection.execute("SELECT 1 FROM dhan_structured_rebuild_checkpoints WHERE cohort=? AND instrument_id=? AND timeframe=? AND persistence_version=? AND status='COMPLETE'", (cohort,instrument_id,timeframe,version)).fetchone() is not None

    def checkpoint_structured_rebuild(self, cohort: str, instrument_id: str, timeframe: str, version: str) -> None:
        with self.connection() as connection:
            connection.execute("INSERT INTO dhan_structured_rebuild_checkpoints VALUES (?,?,?,?,?,?) ON CONFLICT(cohort,instrument_id,timeframe,persistence_version) DO UPDATE SET status='COMPLETE',updated_at=excluded.updated_at", (cohort,instrument_id,timeframe,version,"COMPLETE",datetime.now(UTC).isoformat()))
            connection.commit()

    def exclude_active_zone_instrument(self, cohort: str, instrument_id: str, timeframe: str, reason_code: str) -> None:
        with self.connection() as connection:
            connection.execute("INSERT INTO dhan_active_zone_exclusions VALUES (?,?,?,?,?) ON CONFLICT(cohort,instrument_id,timeframe) DO UPDATE SET reason_code=excluded.reason_code,excluded_at=excluded.excluded_at", (cohort,instrument_id,timeframe,reason_code,datetime.now(UTC).isoformat()))
            connection.commit()

    def canonical_covers_persisted_source(self, cohort: str, instrument_id: str, timeframe: str) -> bool:
        """Reuse committed work only when no source candle changed after it.

        Unchanged merges retain retrieved_at; revisions advance it. Include
        Daily source revisions for derived EOD candles as well as the frame.
        """
        with self.connection() as connection:
            row = connection.execute(
                """SELECT julianday(c.updated_at) >= MAX(julianday(s.retrieved_at))
                FROM dhan_canonical_checkpoints c JOIN dhan_shadow_candles s
                  ON s.instrument_id=c.instrument_id AND s.timeframe IN ('1D',?)
                WHERE c.cohort=? AND c.instrument_id=? AND c.timeframe=?
                  AND c.status='COMPLETE' GROUP BY c.updated_at""",
                (timeframe, cohort, instrument_id, timeframe),
            ).fetchone()
        return row is not None and row[0] == 1

    def save_canonical(self, cohort: str, instrument: DhanInstrument, timeframe: str, zones: list[object]) -> None:
        now = datetime.now(UTC).isoformat()
        payload = [self._structured_payload(zone) for zone in zones]
        with self._lock, self.connection() as connection:
            connection.execute("DELETE FROM dhan_shadow_zones WHERE cohort=? AND instrument_id=? AND timeframe=?", (cohort,instrument.instrument_id,timeframe))
            connection.executemany("INSERT INTO dhan_shadow_zones VALUES (?,?,?,?,?,?)", [(cohort,instrument.instrument_id,timeframe,str(i),json.dumps(item, default=str),now) for i,item in enumerate(payload)])
            connection.execute("INSERT INTO dhan_canonical_checkpoints VALUES (?,?,?,?,?,?,?) ON CONFLICT(cohort,instrument_id,timeframe) DO UPDATE SET status='COMPLETE',zone_count=excluded.zone_count,updated_at=excluded.updated_at,error_code=NULL", (cohort,instrument.instrument_id,timeframe,"COMPLETE",len(payload),now,None))
            connection.commit()

    @classmethod
    def _structured_payload(cls, value: object) -> object:
        """Encode analytical evidence as JSON data, never Python repr strings."""
        if isinstance(value, Enum):
            return value.value
        if is_dataclass(value):
            return {key: cls._structured_payload(item) for key, item in asdict(value).items()}
        if isinstance(value, dict):
            return {str(key): cls._structured_payload(item) for key, item in value.items()}
        if isinstance(value, (tuple, list)):
            return [cls._structured_payload(item) for item in value]
        return value

    def publish_materialization(self, snapshot_id: int, processed: int, zones: int, qualified: int, source_fingerprint: str = "dhan-candles") -> None:
        with self.connection() as connection:
            connection.execute("UPDATE dhan_materialization_snapshots SET status='COMPLETE',processed_instruments=?,zone_count=?,qualified_count=?,completed_at=?,source_fingerprint=? WHERE snapshot_id=? AND status='BUILDING'", (processed,zones,qualified,datetime.now(UTC).isoformat(),source_fingerprint,snapshot_id))
            connection.commit()

    def canonical_accounting(self, cohort: str, timeframe: str) -> dict[str, int]:
        with self.connection() as connection:
            completed = connection.execute(
                "SELECT COUNT(*) FROM dhan_canonical_checkpoints WHERE cohort=? AND timeframe=? AND status='COMPLETE'",
                (cohort, timeframe),
            ).fetchone()[0]
            exclusions = connection.execute(
                "SELECT status,COUNT(*) FROM dhan_canonical_terminal_exclusions WHERE cohort=? AND timeframe=? GROUP BY status",
                (cohort, timeframe),
            ).fetchall()
            zones = connection.execute(
                "SELECT COUNT(*) FROM dhan_shadow_zones WHERE cohort=? AND timeframe=?",
                (cohort, timeframe),
            ).fetchone()[0]
        result = {"SUCCESS": int(completed), "zones": int(zones)}
        result.update({str(row[0]): int(row[1]) for row in exclusions})
        return result

    def active_structured_zone_payloads(
        self, cohort: str, timeframe: str
    ) -> list[sqlite3.Row]:
        """Read active structured canonical records only; archive rows stay untouched."""
        with self.connection() as connection:
            return connection.execute(
                """SELECT z.instrument_id,z.zone_identity,z.payload,i.symbol,i.exchange
                FROM dhan_shadow_zones z JOIN dhan_instruments i ON i.instrument_id=z.instrument_id
                LEFT JOIN dhan_active_zone_exclusions e
                  ON e.cohort=z.cohort AND e.instrument_id=z.instrument_id AND e.timeframe=z.timeframe
                WHERE z.cohort=? AND z.timeframe=? AND e.instrument_id IS NULL
                ORDER BY z.instrument_id,z.zone_identity""",
                (cohort,timeframe),
            ).fetchall()

    def active_structured_zone_payloads_for_instrument(
        self, cohort: str, timeframe: str, instrument_id: str,
    ) -> list[sqlite3.Row]:
        """Read one active instrument's typed canonical payloads only."""
        with self.connection() as connection:
            return connection.execute(
                """SELECT z.instrument_id,z.zone_identity,z.payload,i.symbol,i.exchange
                FROM dhan_shadow_zones z JOIN dhan_instruments i ON i.instrument_id=z.instrument_id
                LEFT JOIN dhan_active_zone_exclusions e
                  ON e.cohort=z.cohort AND e.instrument_id=z.instrument_id AND e.timeframe=z.timeframe
                WHERE z.cohort=? AND z.timeframe=? AND z.instrument_id=?
                  AND e.instrument_id IS NULL
                ORDER BY z.zone_identity""",
                (cohort, timeframe, instrument_id),
            ).fetchall()

    def active_canonical_instruments(self, cohort: str, timeframe: str) -> list[sqlite3.Row]:
        """Current-master instruments with completed canonical output only."""
        with self.connection() as connection:
            return connection.execute(
                """SELECT c.instrument_id,i.symbol,i.exchange
                FROM dhan_canonical_checkpoints c JOIN dhan_instruments i ON i.instrument_id=c.instrument_id
                LEFT JOIN dhan_active_zone_exclusions e
                  ON e.cohort=c.cohort AND e.instrument_id=c.instrument_id AND e.timeframe=c.timeframe
                WHERE c.cohort=? AND c.timeframe=? AND c.status='COMPLETE' AND e.instrument_id IS NULL
                ORDER BY c.instrument_id""",
                (cohort,timeframe),
            ).fetchall()

    def active_instrument_for_symbol(self, symbol: str) -> sqlite3.Row | None:
        """Resolve a current Dhan master symbol without guessing an identity."""
        with self.connection() as connection:
            return connection.execute(
                """SELECT instrument_id,symbol,exchange FROM dhan_instruments
                WHERE symbol=? AND provider_addressable=1
                ORDER BY CASE exchange WHEN 'NSE' THEN 0 ELSE 1 END,instrument_id
                LIMIT 1""",
                (symbol.strip().upper(),),
            ).fetchone()

    def active_instrument_by_id(self, instrument_id: str) -> sqlite3.Row | None:
        with self.connection() as connection:
            return connection.execute(
                """SELECT instrument_id,symbol,exchange FROM dhan_instruments
                WHERE instrument_id=? AND provider_addressable=1""",
                (instrument_id,),
            ).fetchone()

    def instruments_by_ids(self, instrument_ids: list[str]) -> list[DhanInstrument]:
        """Read exact current-master identities for a runtime quote request."""
        if not instrument_ids:
            return []
        placeholders = ",".join("?" for _ in instrument_ids)
        with self.connection() as connection:
            rows = connection.execute(
                f"""SELECT exchange,security_id,symbol,isin,series,category,display_name
                    FROM dhan_instruments WHERE instrument_id IN ({placeholders})
                      AND provider_addressable=1 ORDER BY instrument_id""",
                instrument_ids,
            ).fetchall()
        return [
            DhanInstrument(
                exchange=str(row["exchange"]), security_id=str(row["security_id"]),
                symbol=str(row["symbol"]), isin=str(row["isin"]),
                series=str(row["series"]), category=str(row["category"]),
                display_name=str(row["display_name"]),
            )
            for row in rows
        ]

    def search_current_instruments(self, query: str, limit: int = 10) -> list[dict[str, object]]:
        """Search the current Dhan master, independently of qualifying zones."""
        normalized = query.strip().upper()
        if not normalized:
            return []
        prefix, pattern = f"{normalized}%", f"%{normalized}%"
        with self.connection() as connection:
            rows = connection.execute(
                """SELECT instrument_id,exchange,symbol AS exchange_symbol,
                          symbol AS display_symbol,display_name AS instrument_name,
                          isin,series,provider_addressable AS is_active,
                          security_id AS provider_identifier,
                          CASE WHEN symbol=? THEN 0 WHEN symbol LIKE ? THEN 1
                               WHEN upper(display_name) LIKE ? THEN 2 ELSE 3 END AS relevance
                   FROM dhan_instruments
                   WHERE provider_addressable=1
                     AND (symbol LIKE ? OR upper(display_name) LIKE ? OR isin LIKE ?)
                   ORDER BY relevance,exchange,symbol,instrument_id LIMIT ?""",
                (normalized, prefix, prefix, pattern, pattern, pattern, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def latest_daily_closes(self, instrument_ids: list[str]) -> dict[str, tuple[float, str]]:
        """Return latest persisted Dhan Daily close and source timestamp."""
        if not instrument_ids:
            return {}
        placeholders = ",".join("?" for _ in instrument_ids)
        with self.connection() as connection:
            rows = connection.execute(
                f"""SELECT c.instrument_id,c.close,c.timestamp
                    FROM dhan_shadow_candles c JOIN (
                      SELECT instrument_id,MAX(timestamp) AS timestamp
                      FROM dhan_shadow_candles WHERE timeframe='1D'
                        AND instrument_id IN ({placeholders}) GROUP BY instrument_id
                    ) latest ON latest.instrument_id=c.instrument_id AND latest.timestamp=c.timestamp
                    WHERE c.timeframe='1D'""",
                instrument_ids,
            ).fetchall()
        return {str(row["instrument_id"]): (float(row["close"]), str(row["timestamp"])) for row in rows}

    @staticmethod
    def _universe_predicate(
        universe: str, constituent_symbols: list[str] | tuple[str, ...] = ()
    ) -> tuple[str, list[object]]:
        """Return a Dhan-master predicate; identities never collapse by symbol."""
        normalized = universe.lower()
        category_predicates = {
            "nse_main": ("i.category='NSE_MAIN'", []),
            "nse_sme": ("i.category='NSE_SME'", []),
            "allnse": ("i.exchange='NSE'", []),
            "bse_main": ("i.category='BSE_MAIN'", []),
            "bse_sme": ("i.category='BSE_SME'", []),
            "allbse": ("i.exchange='BSE'", []),
            "allindia": ("i.exchange IN ('NSE','BSE')", []),
        }
        if normalized in category_predicates:
            return category_predicates[normalized]
        symbols = sorted({symbol.strip().upper() for symbol in constituent_symbols if symbol.strip()})
        if normalized in {"nifty50", "nifty100", "nifty200", "nse500", "fno"}:
            if not symbols:
                return "0", []
            placeholders = ",".join("?" for _ in symbols)
            return f"i.exchange='NSE' AND i.symbol IN ({placeholders})", list(symbols)
        raise ValueError(f"Unsupported Dhan equity universe: {universe}")

    def current_master_universe_counts(
        self, constituent_symbols: dict[str, list[str] | tuple[str, ...]]
    ) -> dict[str, int]:
        """Count active Dhan identities, not legacy/static symbol-master rows."""
        result: dict[str, int] = {}
        for universe in (
            "nifty50", "nifty100", "nifty200", "nse500", "fno",
            "nse_main", "nse_sme", "allnse", "bse_main", "bse_sme",
            "allbse", "allindia",
        ):
            predicate, values = self._universe_predicate(
                universe, constituent_symbols.get(universe, ())
            )
            with self.connection() as connection:
                result[universe] = int(connection.execute(
                    f"SELECT COUNT(*) FROM dhan_instruments i "
                    f"WHERE i.provider_addressable=1 AND {predicate}", values
                ).fetchone()[0])
        return result

    def begin_dashboard_result_snapshot(
        self, cohort: str, timeframe: str, total_instruments: int, *,
        methodology_version: str,
    ) -> int:
        with self.connection() as connection:
            cursor = connection.execute(
                """INSERT INTO dhan_dashboard_result_snapshots
                (cohort,timeframe,status,total_instruments,created_at,methodology_version)
                VALUES (?,?,?,?,?,?)""",
                (cohort,timeframe,"BUILDING",total_instruments,datetime.now(UTC).isoformat(),methodology_version),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def latest_building_dashboard_result_snapshot(self, cohort: str, timeframe: str, methodology_version: str) -> int | None:
        with self.connection() as connection:
            row = connection.execute(
                """SELECT snapshot_id FROM dhan_dashboard_result_snapshots
                WHERE provider='dhan' AND cohort=? AND timeframe=? AND status='BUILDING' AND methodology_version=?
                ORDER BY snapshot_id DESC LIMIT 1""",
                (cohort,timeframe,methodology_version),
            ).fetchone()
            return int(row[0]) if row else None

    def abandon_dashboard_result_snapshot(self, snapshot_id: int, reason: str) -> None:
        """Prevent an invalid BUILDING result snapshot from ever publishing."""
        with self.connection() as connection:
            connection.execute(
                """UPDATE dhan_dashboard_result_snapshots
                SET status='FAILED', completed_at=?
                WHERE snapshot_id=? AND status='BUILDING'""",
                (datetime.now(UTC).isoformat(), snapshot_id),
            )
            connection.commit()

    def write_dashboard_result_rows(self, snapshot_id: int, rows: list[tuple[str,str,str,str,str,str|None,float,float|None,float,bool,str]]) -> None:
        if not rows:
            return
        with self._lock, self.connection() as connection:
            connection.executemany(
                """INSERT OR REPLACE INTO dhan_dashboard_result_rows
                (snapshot_id,row_id,instrument_id,symbol,exchange,zone_type,pattern_type,zone_quality,trade_confidence,distance_percent,dashboard_qualified,payload)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                [(snapshot_id,*row) for row in rows],
            )
            connection.commit()

    def copy_dashboard_result_rows(self, source_snapshot_id: int, target_snapshot_id: int) -> None:
        """Copy a READY result set into a BUILDING snapshot for atomic repair."""
        with self._lock, self.connection() as connection:
            connection.execute(
                """INSERT INTO dhan_dashboard_result_rows
                SELECT ?,row_id,instrument_id,symbol,exchange,zone_type,pattern_type,
                       zone_quality,trade_confidence,distance_percent,dashboard_qualified,payload
                FROM dhan_dashboard_result_rows WHERE snapshot_id=?""",
                (target_snapshot_id, source_snapshot_id),
            )
            connection.commit()

    def replace_dashboard_instrument_rows(
        self, snapshot_id: int, instrument_id: str,
        rows: list[tuple[str,str,str,str,str,str|None,float,float|None,float,bool,str]],
    ) -> None:
        """Replace only one instrument in a BUILDING result snapshot atomically."""
        with self._lock, self.connection() as connection:
            connection.execute(
                "DELETE FROM dhan_dashboard_result_rows WHERE snapshot_id=? AND instrument_id=?",
                (snapshot_id, instrument_id),
            )
            if rows:
                connection.executemany(
                    """INSERT INTO dhan_dashboard_result_rows
                    (snapshot_id,row_id,instrument_id,symbol,exchange,zone_type,pattern_type,zone_quality,trade_confidence,distance_percent,dashboard_qualified,payload)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    [(snapshot_id, *row) for row in rows],
                )
            connection.commit()

    def replace_dashboard_instruments_rows(
        self, snapshot_id: int, replacements: dict[str, list[tuple]],
    ) -> None:
        """Replace a bounded instrument batch in one SQLite transaction."""
        if not replacements:
            return
        now = datetime.now(UTC).isoformat()
        with self._lock, self.connection() as connection:
            connection.executemany(
                "DELETE FROM dhan_dashboard_result_rows WHERE snapshot_id=? AND instrument_id=?",
                [(snapshot_id, instrument_id) for instrument_id in replacements],
            )
            rows = [
                (snapshot_id, *row)
                for values in replacements.values() for row in values
            ]
            if rows:
                connection.executemany(
                    """INSERT INTO dhan_dashboard_result_rows
                    (snapshot_id,row_id,instrument_id,symbol,exchange,zone_type,pattern_type,zone_quality,trade_confidence,distance_percent,dashboard_qualified,payload)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    rows,
                )
            connection.executemany(
                """INSERT INTO dhan_dashboard_result_checkpoints VALUES (?,?,?,?,?)
                ON CONFLICT(snapshot_id,instrument_id) DO UPDATE SET
                status=excluded.status,error_code=excluded.error_code,updated_at=excluded.updated_at""",
                [(snapshot_id, instrument_id, "COMPLETE", None, now)
                 for instrument_id in replacements],
            )
            connection.commit()

    def checkpoint_dashboard_instrument(
        self, snapshot_id: int, instrument_id: str, status: str, error_code: str | None = None,
    ) -> None:
        self.checkpoint_dashboard_result(snapshot_id, instrument_id, status, error_code)

    def update_dashboard_result_payloads(
        self, snapshot_id: int, payloads: dict[str, str]
    ) -> None:
        if not payloads:
            return
        with self._lock, self.connection() as connection:
            connection.executemany(
                """UPDATE dhan_dashboard_result_rows SET payload=?
                WHERE snapshot_id=? AND row_id=?""",
                [(payload, snapshot_id, row_id) for row_id, payload in payloads.items()],
            )
            connection.commit()

    def dashboard_result_row_count(self, snapshot_id: int) -> int:
        with self.connection() as connection:
            return int(
                connection.execute(
                    "SELECT COUNT(*) FROM dhan_dashboard_result_rows WHERE snapshot_id=?",
                    (snapshot_id,),
                ).fetchone()[0]
            )

    def checkpoint_dashboard_result(self, snapshot_id: int, instrument_id: str, status: str, error_code: str | None = None) -> None:
        with self._lock, self.connection() as connection:
            connection.execute(
                """INSERT INTO dhan_dashboard_result_checkpoints VALUES (?,?,?,?,?)
                ON CONFLICT(snapshot_id,instrument_id) DO UPDATE SET status=excluded.status,error_code=excluded.error_code,updated_at=excluded.updated_at""",
                (snapshot_id,instrument_id,status,error_code,datetime.now(UTC).isoformat()),
            )
            connection.commit()

    def dashboard_checkpoint_complete(self, snapshot_id: int, instrument_id: str) -> bool:
        with self.connection() as connection:
            return connection.execute(
                "SELECT 1 FROM dhan_dashboard_result_checkpoints WHERE snapshot_id=? AND instrument_id=? AND status='COMPLETE'",
                (snapshot_id,instrument_id),
            ).fetchone() is not None

    def publish_dashboard_result_snapshot(
        self, snapshot_id: int, *, processed: int, results: int, exclusions: int = 0,
    ) -> None:
        with self.connection() as connection:
            connection.execute(
                """UPDATE dhan_dashboard_result_snapshots SET status='READY',processed_instruments=?,result_count=?,exclusion_count=?,completed_at=?
                WHERE snapshot_id=? AND status='BUILDING'""",
                (processed,results,exclusions,datetime.now(UTC).isoformat(),snapshot_id),
            )
            connection.commit()

    def latest_ready_dashboard_result_snapshot(self, cohort: str, timeframe: str) -> sqlite3.Row | None:
        with self.connection() as connection:
            return connection.execute(
                """SELECT * FROM dhan_dashboard_result_snapshots WHERE provider='dhan' AND cohort=? AND timeframe=? AND status='READY'
                ORDER BY snapshot_id DESC LIMIT 1""", (cohort,timeframe)
            ).fetchone()

    def dashboard_snapshot_statuses(self, cohort: str) -> dict[str, dict[str, object]]:
        """Return the latest state per timeframe without triggering any work."""
        with self.connection() as connection:
            rows = connection.execute(
                """SELECT s.* FROM dhan_dashboard_result_snapshots s
                JOIN (
                    SELECT timeframe,MAX(snapshot_id) AS snapshot_id
                    FROM dhan_dashboard_result_snapshots
                    WHERE provider='dhan' AND cohort=? GROUP BY timeframe
                ) latest ON latest.snapshot_id=s.snapshot_id
                ORDER BY s.timeframe""",
                (cohort,),
            ).fetchall()
        return {
            str(row["timeframe"]): {
                "snapshot_id": int(row["snapshot_id"]), "status": str(row["status"]),
                "completed_at": row["completed_at"], "result_count": int(row["result_count"]),
            }
            for row in rows
        }

    def latest_candle_timestamp(self, timeframe: str = "1D") -> str | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT MAX(timestamp) FROM dhan_shadow_candles WHERE timeframe=?", (timeframe,)
            ).fetchone()
        return str(row[0]) if row and row[0] is not None else None

    def begin_incremental_update_run(self, *, stale_after_seconds: int = 21600) -> int | None:
        """Acquire a durable single-run lock; stale interrupted runs are failed safely."""
        now = datetime.now(UTC)
        cutoff = (now - pd.Timedelta(seconds=stale_after_seconds)).isoformat()
        with self._lock, self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            running = connection.execute(
                "SELECT run_id FROM dhan_incremental_update_runs WHERE status IN ('RUNNING','CANCELLING') AND started_at>=? ORDER BY run_id DESC LIMIT 1",
                (cutoff,),
            ).fetchone()
            if running is not None:
                connection.commit()
                return None
            connection.execute(
                """UPDATE dhan_incremental_update_runs SET status='FAILED', completed_at=?, error='INTERRUPTED_STALE_RUN'
                WHERE status IN ('RUNNING','CANCELLING') AND started_at<?""",
                (now.isoformat(), cutoff),
            )
            cursor = connection.execute(
                "INSERT INTO dhan_incremental_update_runs(status,stage,started_at) VALUES ('RUNNING','Checking Dhan...',?)",
                (now.isoformat(),),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def finish_incremental_update_run(
        self, run_id: int, *, status: str, instruments_checked: int,
        instruments_changed: int, instruments_failed: int, error: str | None = None,
    ) -> None:
        if status not in {"READY", "FAILED", "CANCELLED"}:
            raise ValueError("Incremental update must finish READY, FAILED, or CANCELLED.")
        with self._lock, self.connection() as connection:
            connection.execute(
                """UPDATE dhan_incremental_update_runs SET status=?,stage=?,completed_at=?,latest_trading_date=?,
                instruments_checked=?,instruments_changed=?,instruments_failed=?,error=?
                WHERE run_id=? AND status IN ('RUNNING','CANCELLING')""",
                (status, "Update complete" if status == "READY" else "Update cancelled" if status == "CANCELLED" else "Update failed",
                 datetime.now(UTC).isoformat(), self.latest_candle_timestamp(),
                 instruments_checked, instruments_changed, instruments_failed, error, run_id),
            )
            connection.commit()

    def set_incremental_update_stage(self, run_id: int, stage: str) -> None:
        with self._lock, self.connection() as connection:
            connection.execute(
                "UPDATE dhan_incremental_update_runs SET stage=? WHERE run_id=? AND status IN ('RUNNING','CANCELLING')",
                (stage, run_id),
            )
            connection.commit()

    def set_incremental_update_progress(
        self, run_id: int, *, stage: str, completed: int, total: int,
        affected_timeframes: tuple[str, ...] = (),
    ) -> None:
        """Persist actual worker progress for every Dashboard/tab to read."""
        with self._lock, self.connection() as connection:
            connection.execute(
                """UPDATE dhan_incremental_update_runs
                SET stage=?, progress_completed=?, progress_total=?, affected_timeframes=?
                WHERE run_id=? AND status IN ('RUNNING','CANCELLING')""",
                (
                    stage, max(0, completed), max(0, total),
                    ",".join(affected_timeframes), run_id,
                ),
            )
            connection.commit()

    def request_incremental_update_cancellation(self, run_id: int) -> bool:
        """Request a graceful stop for one exact active update run.

        The worker retains the durable lock until it observes this request at
        a safe boundary and finalizes the run as CANCELLED.
        """
        with self._lock, self.connection() as connection:
            cursor = connection.execute(
                """UPDATE dhan_incremental_update_runs
                SET status='CANCELLING', stage='Cancelling update...', cancellation_requested_at=?
                WHERE run_id=? AND status='RUNNING'""",
                (datetime.now(UTC).isoformat(), run_id),
            )
            if cursor.rowcount == 0:
                row = connection.execute(
                    "SELECT status FROM dhan_incremental_update_runs WHERE run_id=?", (run_id,)
                ).fetchone()
                connection.commit()
                return row is not None and str(row[0]) == "CANCELLING"
            connection.commit()
            return True

    def incremental_update_cancellation_requested(self, run_id: int) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT status FROM dhan_incremental_update_runs WHERE run_id=?", (run_id,)
            ).fetchone()
        return row is not None and str(row[0]) == "CANCELLING"

    def incremental_update_status(self) -> dict[str, object]:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM dhan_incremental_update_runs ORDER BY run_id DESC LIMIT 1"
            ).fetchone()
        result = dict(row) if row is not None else {
            "status": "READY", "stage": "READY", "started_at": None, "completed_at": None,
            "latest_trading_date": self.latest_candle_timestamp(),
            "instruments_checked": 0, "instruments_changed": 0, "instruments_failed": 0,
            "progress_completed": 0, "progress_total": 0, "affected_timeframes": "",
            "error": None,
        }
        result["latest_trading_date"] = result.get("latest_trading_date") or self.latest_candle_timestamp()
        return result

    def latest_successful_incremental_update_at(self) -> str | None:
        with self.connection() as connection:
            row = connection.execute(
                """SELECT completed_at FROM dhan_incremental_update_runs
                WHERE status='READY' AND completed_at IS NOT NULL
                ORDER BY run_id DESC LIMIT 1"""
            ).fetchone()
        return str(row[0]) if row is not None and row[0] is not None else None

    def mark_incremental_dirty(
        self, instrument_id: str, timeframe: str, reason_code: str,
        earliest_changed_timestamp: str | None = None,
    ) -> None:
        with self._lock, self.connection() as connection:
            connection.execute(
                """INSERT INTO dhan_incremental_dirty_instruments
                (instrument_id,timeframe,reason_code,updated_at,earliest_changed_timestamp)
                VALUES (?,?,?,?,?) ON CONFLICT(instrument_id,timeframe) DO UPDATE SET
                reason_code=excluded.reason_code,updated_at=excluded.updated_at,
                earliest_changed_timestamp=CASE
                  WHEN dhan_incremental_dirty_instruments.earliest_changed_timestamp IS NULL
                    THEN excluded.earliest_changed_timestamp
                  WHEN excluded.earliest_changed_timestamp IS NULL
                    THEN dhan_incremental_dirty_instruments.earliest_changed_timestamp
                  ELSE MIN(dhan_incremental_dirty_instruments.earliest_changed_timestamp,
                           excluded.earliest_changed_timestamp) END""",
                (
                    instrument_id, timeframe, reason_code,
                    datetime.now(UTC).isoformat(), earliest_changed_timestamp,
                ),
            )
            connection.commit()

    def dirty_incremental_instruments(self, timeframe: str) -> list[str]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT instrument_id FROM dhan_incremental_dirty_instruments WHERE timeframe=? ORDER BY instrument_id",
                (timeframe,),
            ).fetchall()
        return [str(row[0]) for row in rows]

    def dirty_incremental_work(self, timeframe: str) -> dict[str, str | None]:
        """Return resumable identities with their earliest affected source bar."""
        with self.connection() as connection:
            rows = connection.execute(
                """SELECT instrument_id,earliest_changed_timestamp
                FROM dhan_incremental_dirty_instruments
                WHERE timeframe=? ORDER BY instrument_id""", (timeframe,),
            ).fetchall()
        return {
            str(row["instrument_id"]): (
                str(row["earliest_changed_timestamp"])
                if row["earliest_changed_timestamp"] is not None else None
            )
            for row in rows
        }

    def clear_incremental_dirty(self, instrument_ids: list[str], timeframe: str) -> None:
        if not instrument_ids:
            return
        placeholders = ",".join("?" for _ in instrument_ids)
        with self._lock, self.connection() as connection:
            connection.execute(
                f"DELETE FROM dhan_incremental_dirty_instruments WHERE timeframe=? AND instrument_id IN ({placeholders})",
                [timeframe, *instrument_ids],
            )
            connection.commit()

    def record_pathological_instrument(
        self, *, run_id: int, instrument_id: str, timeframe: str,
        symbol: str, candle_count: int, zone_count: int, stage: str,
        elapsed_seconds: float, attempt: int, result: str,
    ) -> None:
        """Persist credential-free timing evidence for one isolated calculation."""
        with self._lock, self.connection() as connection:
            connection.execute(
                """INSERT INTO dhan_incremental_pathological_instruments
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(run_id,instrument_id,timeframe,attempt) DO UPDATE SET
                    candle_count=excluded.candle_count,
                    zone_count=excluded.zone_count,
                    stage=excluded.stage,
                    elapsed_seconds=excluded.elapsed_seconds,
                    result=excluded.result,
                    recorded_at=excluded.recorded_at""",
                (
                    run_id, instrument_id, timeframe, symbol, candle_count,
                    zone_count, stage, elapsed_seconds, attempt, result,
                    datetime.now(UTC).isoformat(),
                ),
            )
            connection.commit()

    def query_dashboard_result_rows(
        self, snapshot_id: int, *, zone_type: str | None, pattern: str | None,
        min_zone_quality: float | None, min_trade_confidence: float | None,
        status: str | None, symbol: str | None, max_distance: float | None,
        sort: str, descending: bool, page: int, page_size: int,
        universe: str = "allindia",
        universe_symbols: list[str] | tuple[str, ...] = (),
    ) -> tuple[int, list[str]]:
        columns = {
            "contextual_rank": "r.distance_percent ASC, r.zone_quality DESC, r.symbol ASC, r.row_id ASC",
            "trade_confidence": "r.trade_confidence", "zone_quality": "r.zone_quality",
            "distance": "r.distance_percent",
            "current_price": "CAST(json_extract(r.payload,'$.current_price') AS REAL)",
            "symbol": "r.symbol",
        }
        if sort not in columns:
            raise ValueError("Unsupported sort.")
        universe_predicate, universe_values = self._universe_predicate(universe, universe_symbols)
        clauses, values = ["r.snapshot_id=?", "r.dashboard_qualified=1", "i.provider_addressable=1", universe_predicate], [snapshot_id, *universe_values]
        if zone_type: clauses.append("r.zone_type=?"); values.append(zone_type.upper())
        if pattern: clauses.append("r.pattern_type=?"); values.append(pattern.upper())
        if min_zone_quality is not None: clauses.append("r.zone_quality>=?"); values.append(min_zone_quality)
        if min_trade_confidence is not None: clauses.append("r.trade_confidence>=?"); values.append(min_trade_confidence)
        if status: clauses.append("json_extract(r.payload,'$.status')=?"); values.append(status)
        if symbol: clauses.append("r.symbol LIKE ?"); values.append(f"%{symbol.upper()}%")
        if max_distance is not None: clauses.append("r.distance_percent<=?"); values.append(max_distance)
        where = " AND ".join(clauses)
        if sort == "contextual_rank" and not descending:
            order = columns[sort]
        else:
            direction = "DESC" if descending else "ASC"
            # SQLite sorts NULL first in ascending order.  Missing numerical
            # values must always remain after available Dashboard values.
            null_last = f"CASE WHEN {columns[sort]} IS NULL THEN 1 ELSE 0 END"
            order = f"{null_last} ASC, {columns[sort]} {direction}, r.symbol ASC, r.row_id ASC"
        with self.connection() as connection:
            source = "dhan_dashboard_result_rows r JOIN dhan_instruments i ON i.instrument_id=r.instrument_id"
            total = int(connection.execute(f"SELECT COUNT(*) FROM {source} WHERE {where}", values).fetchone()[0])
            rows = connection.execute(
                f"SELECT json_set(r.payload,'$.instrument_id',r.instrument_id) FROM {source} WHERE {where} ORDER BY {order} LIMIT ? OFFSET ?",
                [*values,page_size,(page-1)*page_size],
            ).fetchall()
        return total, [str(row[0]) for row in rows]

    def synchronize_master(self, instruments: tuple[DhanInstrument, ...]) -> None:
        now = datetime.now(UTC).isoformat()
        with self._lock, self.connection() as connection:
            connection.executemany(
                """INSERT INTO dhan_instruments VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(instrument_id) DO UPDATE SET symbol=excluded.symbol,
                isin=excluded.isin, series=excluded.series, category=excluded.category,
                display_name=excluded.display_name, provider_addressable=1,
                synchronized_at=excluded.synchronized_at""",
                [
                    (
                        i.instrument_id,
                        i.exchange,
                        i.security_id,
                        i.symbol,
                        i.isin,
                        i.series,
                        i.category,
                        i.display_name,
                        now,
                    )
                    for i in instruments
                ],
            )
            connection.commit()

    def merge(
        self,
        instrument: DhanInstrument,
        timeframe: str,
        source_interval: str,
        frame: DataFrame,
        *,
        semantics: str,
    ) -> ShadowMergeResult:
        inserted = corrected = unchanged = rejected = 0
        now = datetime.now(UTC).isoformat()
        # Dhan has returned duplicate BSE timestamps. Collapse exact duplicate
        # rows deterministically; conflicting rows are recorded and excluded
        # rather than choosing one arbitrarily.
        duplicate_conflicts: list[tuple[str, int, str]] = []
        if frame.index.has_duplicates:
            duplicate_rows = frame[frame.index.duplicated(keep=False)]
            for stamp, group in duplicate_rows.groupby(level=0, sort=False):
                comparable = group[["Open", "High", "Low", "Close", "Volume"]].astype(object)
                if len(comparable.drop_duplicates()) > 1:
                    duplicate_conflicts.append(
                        (
                            pd.Timestamp(stamp).isoformat(),
                            len(group),
                            comparable.reset_index(drop=True).to_json(orient="records"),
                        )
                    )
            conflict_stamps = {stamp for stamp, _, _ in duplicate_conflicts}
            frame = frame[~frame.index.duplicated(keep="first")]
            if conflict_stamps:
                frame = frame[
                    ~frame.index.map(lambda value: pd.Timestamp(value).isoformat()).isin(
                        conflict_stamps
                    )
                ]
        with self._lock, self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for stamp, row_count, evidence in duplicate_conflicts:
                connection.execute(
                    """INSERT INTO dhan_shadow_data_quality_conflicts
                    VALUES (?,?,?,?,?,?)
                    ON CONFLICT(instrument_id,timeframe,timestamp) DO UPDATE SET
                    row_count=excluded.row_count,evidence=excluded.evidence,
                    detected_at=excluded.detected_at""",
                    (instrument.instrument_id, timeframe, stamp, row_count, evidence, now),
                )
                rejected += row_count
            for timestamp, row in frame.sort_index().iterrows():
                try:
                    o, h, l, c = (
                        float(row[key]) for key in ("Open", "High", "Low", "Close")
                    )
                    if (
                        min(o, h, l, c) <= 0
                        or h < l
                        or not (l <= o <= h and l <= c <= h)
                    ):
                        rejected += 1
                        continue
                    volume = (
                        float(row["Volume"]) if pd.notna(row.get("Volume")) else None
                    )
                    quality = "DATA_BREAK" if h == l else "VALID"
                    stamp = pd.Timestamp(timestamp).isoformat()
                except (TypeError, ValueError, KeyError, OverflowError):
                    rejected += 1
                    continue
                previous = connection.execute(
                    "SELECT open,high,low,close,volume,quality_state FROM dhan_shadow_candles WHERE instrument_id=? AND timeframe=? AND timestamp=?",
                    (instrument.instrument_id, timeframe, stamp),
                ).fetchone()
                candidate = (o, h, l, c, volume, quality)
                if previous is None:
                    inserted += 1
                elif tuple(previous) == candidate:
                    unchanged += 1
                    continue
                else:
                    corrected += 1
                connection.execute(
                    """INSERT INTO dhan_shadow_candles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(instrument_id,timeframe,timestamp) DO UPDATE SET
                    open=excluded.open,high=excluded.high,low=excluded.low,close=excluded.close,
                    volume=excluded.volume,quality_state=excluded.quality_state,
                    source_interval=excluded.source_interval,adjustment_semantics=excluded.adjustment_semantics,
                    candle_revision=excluded.candle_revision,retrieved_at=excluded.retrieved_at""",
                    (
                        instrument.instrument_id,
                        timeframe,
                        source_interval,
                        stamp,
                        o,
                        h,
                        l,
                        c,
                        volume,
                        quality,
                        "dhan",
                        semantics,
                        "raw-v1",
                        now,
                    ),
                )
            connection.commit()
        return ShadowMergeResult(inserted, corrected, unchanged, rejected)

    def load(self, instrument_id: str, timeframe: str) -> DataFrame:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT timestamp,open,high,low,close,volume FROM dhan_shadow_candles WHERE instrument_id=? AND timeframe=? ORDER BY timestamp",
                (instrument_id, timeframe),
            ).fetchall()
        frame = DataFrame([dict(row) for row in rows])
        if frame.empty:
            return DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
        frame.index = pd.to_datetime(frame.pop("timestamp"))
        return frame.rename(
            columns={
                name: name.title()
                for name in ("open", "high", "low", "close", "volume")
            }
        )

    def checkpoint(
        self,
        cohort: str,
        instrument: DhanInstrument,
        timeframe: str,
        semantics: str,
        status: str,
        *,
        error_code: str | None = None,
    ) -> None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) n,MIN(timestamp) first,MAX(timestamp) last FROM dhan_shadow_candles WHERE instrument_id=? AND timeframe=?",
                (instrument.instrument_id, timeframe),
            ).fetchone()
            connection.execute(
                """INSERT INTO dhan_shadow_checkpoints VALUES (?,?,?,?,?,?,?,?,1,?,?)
                ON CONFLICT(cohort,instrument_id,timeframe,source_semantics) DO UPDATE SET
                status=excluded.status,candle_count=excluded.candle_count,
                first_timestamp=excluded.first_timestamp,last_timestamp=excluded.last_timestamp,
                attempts=dhan_shadow_checkpoints.attempts+1,error_code=excluded.error_code,
                updated_at=excluded.updated_at""",
                (
                    cohort,
                    instrument.instrument_id,
                    timeframe,
                    semantics,
                    status,
                    int(row["n"]),
                    row["first"],
                    row["last"],
                    error_code,
                    datetime.now(UTC).isoformat(),
                ),
            )
            connection.commit()

    def complete(
        self, cohort: str, instrument_id: str, timeframe: str, semantics: str
    ) -> bool:
        with self.connection() as connection:
            return (
                connection.execute(
                    "SELECT 1 FROM dhan_shadow_checkpoints WHERE cohort=? AND instrument_id=? AND timeframe=? AND source_semantics=? AND status='COMPLETE'",
                    (cohort, instrument_id, timeframe, semantics),
                ).fetchone()
                is not None
            )

    def stats(self, cohort: str, timeframe: str, semantics: str) -> dict[str, int]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT status,COUNT(*) n FROM dhan_shadow_checkpoints WHERE cohort=? AND timeframe=? AND source_semantics=? GROUP BY status",
                (cohort, timeframe, semantics),
            ).fetchall()
        return {row["status"]: int(row["n"]) for row in rows}
