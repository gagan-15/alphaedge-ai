"""Persistent OHLCV storage and deterministic provider-correction merging."""

from __future__ import annotations

import sqlite3
import hashlib
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Iterator

import pandas as pd
from pandas import DataFrame

from backend.services.scanner.persistent_scanner_store import PersistentScannerStore


@dataclass(frozen=True)
class CandleMergeResult:
    inserted: int
    updated: int
    unchanged: int
    rejected: int


class PersistentMarketDataStore:
    """Store canonical provider candles without fabricating or interpolating data."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or PersistentScannerStore().path
        self._lock = RLock()
        self.initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=10000")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._lock, self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS scanner_candles (
                    instrument_id TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    base_timeframe TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL,
                    provider TEXT NOT NULL,
                    data_quality_state TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(instrument_id, base_timeframe, timestamp)
                );
                CREATE INDEX IF NOT EXISTS ix_scanner_candles_latest
                    ON scanner_candles(
                        instrument_id, base_timeframe, timestamp DESC
                    );
                CREATE TABLE IF NOT EXISTS scanner_candle_merge_audit (
                    merge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instrument_id TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    base_timeframe TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    inserted INTEGER NOT NULL,
                    updated INTEGER NOT NULL,
                    unchanged INTEGER NOT NULL,
                    rejected INTEGER NOT NULL,
                    completed_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_candle_merge_audit_lookup
                    ON scanner_candle_merge_audit(
                        instrument_id, base_timeframe, merge_id DESC
                    );
                CREATE TABLE IF NOT EXISTS scanner_source_bootstrap (
                    instrument_id TEXT NOT NULL,
                    base_timeframe TEXT NOT NULL,
                    semantics_version TEXT NOT NULL,
                    requested_period TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN (
                        'COMPLETE','RETRYABLE','FAILED'
                    )),
                    first_timestamp TEXT,
                    last_timestamp TEXT,
                    candle_count INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT,
                    completed_at TEXT NOT NULL,
                    PRIMARY KEY(
                        instrument_id, base_timeframe, semantics_version,
                        requested_period
                    )
                );
                CREATE INDEX IF NOT EXISTS ix_source_bootstrap_status
                    ON scanner_source_bootstrap(
                        semantics_version, requested_period, status,
                        instrument_id
                    );
                """
            )
            connection.commit()

    @staticmethod
    def _timestamp(value: object) -> str:
        stamp = pd.Timestamp(value)
        if stamp.tzinfo is not None:
            stamp = stamp.tz_convert("UTC")
        return stamp.isoformat()

    def latest_timestamp(
        self,
        instrument_id: str,
        timeframe: str,
    ) -> pd.Timestamp | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT timestamp FROM scanner_candles
                WHERE instrument_id=? AND base_timeframe=?
                ORDER BY timestamp DESC LIMIT 1
                """,
                (instrument_id, timeframe),
            ).fetchone()
        return pd.Timestamp(row["timestamp"]) if row else None

    def merge(
        self,
        instrument_id: str,
        exchange: str,
        timeframe: str,
        data: DataFrame,
        *,
        provider: str,
    ) -> CandleMergeResult:
        inserted = updated = unchanged = rejected = 0
        with self._lock, self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for index, row in data.sort_index().iterrows():
                try:
                    values = tuple(
                        float(row[name])
                        for name in ("Open", "High", "Low", "Close")
                    )
                    open_, high, low, close = values
                    if min(values) <= 0 or high < low or not (
                        low <= open_ <= high and low <= close <= high
                    ):
                        rejected += 1
                        continue
                    quality = "DATA_BREAK" if high == low else "VALID"
                    timestamp = self._timestamp(index)
                    volume = (
                        float(row["Volume"])
                        if "Volume" in row and pd.notna(row["Volume"])
                        else None
                    )
                except (KeyError, TypeError, ValueError, OverflowError):
                    rejected += 1
                    continue
                existing = connection.execute(
                    """
                    SELECT open, high, low, close, volume, data_quality_state
                    FROM scanner_candles
                    WHERE instrument_id=? AND base_timeframe=? AND timestamp=?
                    """,
                    (instrument_id, timeframe, timestamp),
                ).fetchone()
                candidate = (open_, high, low, close, volume, quality)
                if existing is None:
                    inserted += 1
                elif tuple(existing) == candidate:
                    unchanged += 1
                    continue
                else:
                    updated += 1
                connection.execute(
                    """
                    INSERT INTO scanner_candles(
                        instrument_id, exchange, base_timeframe, timestamp,
                        open, high, low, close, volume, provider, data_quality_state
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(instrument_id, base_timeframe, timestamp) DO UPDATE SET
                        open=excluded.open, high=excluded.high, low=excluded.low,
                        close=excluded.close, volume=excluded.volume,
                        provider=excluded.provider,
                        data_quality_state=excluded.data_quality_state,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    (
                        instrument_id, exchange, timeframe, timestamp,
                        open_, high, low, close, volume, provider, quality,
                    ),
                )
            result = CandleMergeResult(inserted, updated, unchanged, rejected)
            connection.execute(
                """
                INSERT INTO scanner_candle_merge_audit(
                    instrument_id, exchange, base_timeframe, provider,
                    inserted, updated, unchanged, rejected, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    instrument_id,
                    exchange,
                    timeframe,
                    provider,
                    result.inserted,
                    result.updated,
                    result.unchanged,
                    result.rejected,
                    datetime.now(UTC).isoformat(),
                ),
            )
            capability_table = connection.execute(
                """
                SELECT 1 FROM sqlite_master
                WHERE type='table' AND name='scanner_provider_capabilities'
                """
            ).fetchone()
            if capability_table is not None and (inserted or updated or unchanged):
                connection.execute(
                    """
                    UPDATE scanner_provider_capabilities
                    SET data_status='AVAILABLE', checked_at=?, error_message=NULL
                    WHERE instrument_id=? AND provider=?
                    """,
                    (datetime.now(UTC).isoformat(), instrument_id, provider),
                )
            connection.commit()
        return result

    def merge_totals(self) -> CandleMergeResult:
        """Return durable merge counts for operational verification."""

        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT COALESCE(SUM(inserted), 0) inserted,
                       COALESCE(SUM(updated), 0) updated,
                       COALESCE(SUM(unchanged), 0) unchanged,
                       COALESCE(SUM(rejected), 0) rejected
                FROM scanner_candle_merge_audit
                """
            ).fetchone()
        return CandleMergeResult(
            inserted=int(row["inserted"]),
            updated=int(row["updated"]),
            unchanged=int(row["unchanged"]),
            rejected=int(row["rejected"]),
        )

    def load(self, instrument_id: str, timeframe: str) -> DataFrame:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT timestamp, open, high, low, close, volume
                FROM scanner_candles
                WHERE instrument_id=? AND base_timeframe=?
                ORDER BY timestamp
                """,
                (instrument_id, timeframe),
            ).fetchall()
        if not rows:
            return DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
        frame = DataFrame(
            [dict(row) for row in rows],
        ).rename(
            columns={
                "open": "Open", "high": "High", "low": "Low",
                "close": "Close", "volume": "Volume",
            }
        )
        frame.index = pd.to_datetime(frame.pop("timestamp"))
        return frame

    def revision(self, instrument_id: str, timeframe: str) -> str:
        """Return a stable revision for the exact persisted candle series."""

        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) candle_count, MIN(timestamp) first_timestamp,
                       MAX(timestamp) last_timestamp,
                       COALESCE(MAX(updated_at), '') last_updated,
                       COALESCE(SUM(open), 0) sum_open,
                       COALESCE(SUM(high), 0) sum_high,
                       COALESCE(SUM(low), 0) sum_low,
                       COALESCE(SUM(close), 0) sum_close,
                       COALESCE(SUM(volume), 0) sum_volume
                FROM scanner_candles
                WHERE instrument_id=? AND base_timeframe=?
                """,
                (instrument_id, timeframe),
            ).fetchone()
        identity = "|".join(str(row[key] or "") for key in row.keys())
        return hashlib.sha256(identity.encode("utf-8")).hexdigest()

    def universe_revision(self, timeframe: str) -> str:
        """Return a stable aggregate identity for all persisted source candles."""

        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) candle_count,
                       COUNT(DISTINCT instrument_id) instrument_count,
                       MIN(timestamp) first_timestamp,
                       MAX(timestamp) last_timestamp,
                       COALESCE(MAX(updated_at), '') last_updated,
                       COALESCE(SUM(close), 0) sum_close,
                       COALESCE(SUM(volume), 0) sum_volume
                FROM scanner_candles WHERE base_timeframe=?
                """,
                (timeframe,),
            ).fetchone()
        identity = "|".join(str(row[key] or "") for key in row.keys())
        return hashlib.sha256(identity.encode("utf-8")).hexdigest()

    def mark_bootstrap(
        self,
        instrument_id: str,
        timeframe: str,
        semantics_version: str,
        requested_period: str,
        *,
        status: str,
        error: str | None = None,
    ) -> None:
        """Checkpoint one source-history bootstrap without implying completeness."""

        with self._lock, self._connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) candle_count, MIN(timestamp) first_timestamp,
                       MAX(timestamp) last_timestamp
                FROM scanner_candles
                WHERE instrument_id=? AND base_timeframe=?
                """,
                (instrument_id, timeframe),
            ).fetchone()
            connection.execute(
                """
                INSERT INTO scanner_source_bootstrap(
                    instrument_id, base_timeframe, semantics_version,
                    requested_period, status, first_timestamp, last_timestamp,
                    candle_count, error_message, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(
                    instrument_id, base_timeframe, semantics_version,
                    requested_period
                ) DO UPDATE SET
                    status=excluded.status,
                    first_timestamp=excluded.first_timestamp,
                    last_timestamp=excluded.last_timestamp,
                    candle_count=excluded.candle_count,
                    error_message=excluded.error_message,
                    completed_at=excluded.completed_at
                """,
                (
                    instrument_id, timeframe, semantics_version,
                    requested_period, status, row["first_timestamp"],
                    row["last_timestamp"], int(row["candle_count"]),
                    error[:2000] if error else None,
                    datetime.now(UTC).isoformat(),
                ),
            )
            if status == "FAILED":
                capability_table = connection.execute(
                    """
                    SELECT 1 FROM sqlite_master
                    WHERE type='table' AND name='scanner_provider_capabilities'
                    """
                ).fetchone()
                if capability_table is not None:
                    connection.execute(
                        """
                        UPDATE scanner_provider_capabilities
                        SET data_status='UNAVAILABLE', checked_at=?, error_message=?
                        WHERE instrument_id=?
                        """,
                        (
                            datetime.now(UTC).isoformat(),
                            error[:500] if error else "Provider returned no data.",
                            instrument_id,
                        ),
                    )
            connection.commit()

    def bootstrap_complete(
        self,
        instrument_id: str,
        timeframe: str,
        semantics_version: str,
        requested_period: str,
    ) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT 1 FROM scanner_source_bootstrap
                WHERE instrument_id=? AND base_timeframe=?
                  AND semantics_version=? AND requested_period=?
                  AND status='COMPLETE'
                """,
                (
                    instrument_id, timeframe, semantics_version,
                    requested_period,
                ),
            ).fetchone()
        return row is not None

    def bootstrap_progress(
        self,
        semantics_version: str,
        requested_period: str,
        universe: str | None = None,
    ) -> dict[str, int]:
        with self._connection() as connection:
            if universe:
                rows = connection.execute(
                    """
                    SELECT b.status, COUNT(*) count
                    FROM scanner_source_bootstrap b
                    JOIN scanner_universe_memberships m
                      ON m.instrument_id=b.instrument_id AND m.universe=?
                    WHERE b.semantics_version=? AND b.requested_period=?
                    GROUP BY b.status
                    """,
                    (universe, semantics_version, requested_period),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT status, COUNT(*) count FROM scanner_source_bootstrap
                    WHERE semantics_version=? AND requested_period=?
                    GROUP BY status
                    """,
                    (semantics_version, requested_period),
                ).fetchall()
        return {str(row["status"]): int(row["count"]) for row in rows}
