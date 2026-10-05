"""Persistent, exchange-aware NSE instrument-master synchronization."""

from __future__ import annotations

import csv
import hashlib
import io
import os
import sqlite3
import threading
from dataclasses import dataclass
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

NSE_MAIN_EQUITY_SOURCE = (
    "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
)
NSE_SME_EQUITY_SOURCE = (
    "https://nsearchives.nseindia.com/emerge/corporates/content/SME_EQUITY_L.csv"
)
NSE_SYMBOL_CHANGE_SOURCE = (
    "https://nsearchives.nseindia.com/content/equities/symbolchange.csv"
)
NSE_MAIN_EQUITY_UNIVERSE = "allnse"
NSE_SME_EQUITY_UNIVERSE = "nse_sme"
ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE = "allindia"
NSE_MAIN_EQUITY_SERIES = frozenset({"EQ", "BE", "BZ"})
NSE_SME_EQUITY_SERIES = frozenset({"SM", "ST", "SZ"})
INSTRUMENT_MASTER_ARCHITECTURE_VERSION = "instrument-master-v2-nse-sme"
_SYNC_LEASE_DURATION = timedelta(minutes=5)
_sync_executor = ThreadPoolExecutor(
    max_workers=1, thread_name_prefix="instrument-master-sync"
)
_sync_future: Future[dict[str, object]] | None = None
_sync_future_lock = threading.Lock()


@dataclass(frozen=True)
class InstrumentRecord:
    exchange: str
    symbol: str
    name: str
    isin: str
    series: str
    provider_identifier: str


class InstrumentMasterService:
    """Maintain a last-known-good NSE Main Equity instrument master."""

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
        self._initialize()

    def _connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS scanner_instrument_aliases (
                    exchange TEXT NOT NULL,
                    alias_symbol TEXT NOT NULL,
                    instrument_id TEXT NOT NULL,
                    effective_at TEXT,
                    source TEXT,
                    PRIMARY KEY(exchange, alias_symbol),
                    FOREIGN KEY(instrument_id)
                        REFERENCES scanner_instruments(instrument_id)
                );
                CREATE INDEX IF NOT EXISTS ix_scanner_alias_instrument
                    ON scanner_instrument_aliases(instrument_id);
                CREATE TABLE IF NOT EXISTS scanner_instrument_sync_runs (
                    sync_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    universe TEXT NOT NULL,
                    source TEXT NOT NULL,
                    source_checksum TEXT NOT NULL,
                    source_count INTEGER NOT NULL,
                    imported_count INTEGER NOT NULL,
                    active_count INTEGER NOT NULL,
                    inactive_count INTEGER NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('COMPLETE','FAILED')),
                    started_at TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    error_message TEXT
                );
                CREATE INDEX IF NOT EXISTS ix_instrument_sync_latest
                    ON scanner_instrument_sync_runs(
                        universe, status, sync_id DESC
                    );
                CREATE TABLE IF NOT EXISTS scanner_provider_capabilities (
                    instrument_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    provider_identifier TEXT NOT NULL,
                    mapping_status TEXT NOT NULL,
                    data_status TEXT NOT NULL DEFAULT 'UNKNOWN',
                    checked_at TEXT NOT NULL,
                    error_message TEXT,
                    PRIMARY KEY(instrument_id, provider),
                    FOREIGN KEY(instrument_id)
                        REFERENCES scanner_instruments(instrument_id)
                );
                CREATE TABLE IF NOT EXISTS scanner_instrument_sync_state (
                    universe TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    lease_expires_at TEXT,
                    last_attempt_at TEXT,
                    error_message TEXT
                );
                """
            )

    @staticmethod
    def parse_main_equity(payload: bytes) -> tuple[InstrumentRecord, ...]:
        return InstrumentMasterService._parse_nse_equity(
            payload, allowed_series=NSE_MAIN_EQUITY_SERIES,
            source_name="NSE Main Equity",
        )

    @staticmethod
    def parse_sme_equity(payload: bytes) -> tuple[InstrumentRecord, ...]:
        return InstrumentMasterService._parse_nse_equity(
            payload, allowed_series=NSE_SME_EQUITY_SERIES,
            source_name="NSE SME Equity",
        )

    @staticmethod
    def _parse_nse_equity(
        payload: bytes,
        *,
        allowed_series: frozenset[str],
        source_name: str,
    ) -> tuple[InstrumentRecord, ...]:
        text = payload.decode("utf-8-sig")
        rows = csv.DictReader(io.StringIO(text))
        if rows.fieldnames:
            rows.fieldnames = [
                name.strip().replace("_", " ") for name in rows.fieldnames
            ]
        records: list[InstrumentRecord] = []
        seen_symbols: set[str] = set()
        seen_isins: set[str] = set()
        for row in rows:
            symbol = str(row.get("SYMBOL", "")).strip().upper()
            isin = str(row.get("ISIN NUMBER", "")).strip().upper()
            series = str(row.get("SERIES", "")).strip().upper()
            name = str(row.get("NAME OF COMPANY", "")).strip()
            if (
                not symbol
                or not isin
                or not name
                or series not in allowed_series
            ):
                raise ValueError(
                    f"{source_name} source contains an invalid row: "
                    f"symbol={symbol!r}, series={series!r}, isin={isin!r}."
                )
            if symbol in seen_symbols or isin in seen_isins:
                raise ValueError(
                    f"{source_name} source contains duplicate identity data."
                )
            seen_symbols.add(symbol)
            seen_isins.add(isin)
            records.append(
                InstrumentRecord(
                    exchange="NSE",
                    symbol=symbol,
                    name=name,
                    isin=isin,
                    series=series,
                    provider_identifier=f"{symbol}.NS",
                )
            )
        if not records:
            raise ValueError(f"{source_name} source returned no instruments.")
        return tuple(records)

    @staticmethod
    def parse_symbol_changes(payload: bytes) -> tuple[tuple[str, str, str], ...]:
        rows = csv.reader(io.StringIO(payload.decode("utf-8-sig")))
        return tuple(
            (old.strip().upper(), new.strip().upper(), effective.strip())
            for row in rows
            if len(row) >= 4
            for old, new, effective in [(row[1], row[2], row[3])]
            if old.strip() and new.strip()
        )

    def synchronize(
        self,
        records: tuple[InstrumentRecord, ...],
        *,
        source: str,
        source_checksum: str,
        symbol_changes: tuple[tuple[str, str, str], ...] = (),
    ) -> dict[str, object]:
        return self._synchronize_universe(
            records,
            universe=NSE_MAIN_EQUITY_UNIVERSE,
            instrument_type="MAIN_EQUITY",
            scope="NSE Main Equity (EQ, BE, BZ)",
            allowed_series=NSE_MAIN_EQUITY_SERIES,
            source=source,
            source_checksum=source_checksum,
            symbol_changes=symbol_changes,
        )

    def _synchronize_universe(
        self,
        records: tuple[InstrumentRecord, ...],
        *,
        universe: str,
        instrument_type: str,
        scope: str,
        allowed_series: frozenset[str],
        source: str,
        source_checksum: str,
        symbol_changes: tuple[tuple[str, str, str], ...] = (),
    ) -> dict[str, object]:
        """Atomically replace active membership after full source validation."""

        started = datetime.now(UTC).isoformat()
        current_symbols = {item.symbol for item in records}
        active_ids: set[str] = set()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for record in records:
                existing = connection.execute(
                    """
                    SELECT instrument_id, exchange_symbol
                    FROM scanner_instruments
                    WHERE exchange=? AND isin=?
                    """,
                    (record.exchange, record.isin),
                ).fetchone()
                if existing is None:
                    existing = connection.execute(
                        """
                        SELECT instrument_id, exchange_symbol
                        FROM scanner_instruments
                        WHERE exchange=? AND exchange_symbol=?
                        """,
                        (record.exchange, record.symbol),
                    ).fetchone()
                instrument_id = (
                    str(existing["instrument_id"])
                    if existing is not None
                    else f"{record.exchange}:{record.symbol}"
                )
                if (
                    existing is not None
                    and str(existing["exchange_symbol"]) != record.symbol
                ):
                    connection.execute(
                        """
                        INSERT OR REPLACE INTO scanner_instrument_aliases(
                            exchange, alias_symbol, instrument_id, source
                        ) VALUES (?, ?, ?, ?)
                        """,
                        (
                            record.exchange,
                            str(existing["exchange_symbol"]),
                            instrument_id,
                            source,
                        ),
                    )
                connection.execute(
                    """
                    INSERT INTO scanner_instruments(
                        instrument_id, exchange, exchange_symbol, display_symbol,
                        instrument_name, instrument_type, isin, series, is_active,
                        provider_identifier, metadata_updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                    ON CONFLICT(instrument_id) DO UPDATE SET
                        exchange_symbol=excluded.exchange_symbol,
                        display_symbol=excluded.display_symbol,
                        instrument_name=excluded.instrument_name,
                        instrument_type=excluded.instrument_type,
                        isin=excluded.isin,
                        series=excluded.series,
                        is_active=1,
                        provider_identifier=excluded.provider_identifier,
                        metadata_updated_at=excluded.metadata_updated_at
                    """,
                    (
                        instrument_id,
                        record.exchange,
                        record.symbol,
                        record.symbol,
                        record.name,
                        instrument_type,
                        record.isin,
                        record.series,
                        record.provider_identifier,
                        started,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO scanner_provider_capabilities(
                        instrument_id, provider, provider_identifier,
                        mapping_status, data_status, checked_at
                    ) VALUES (?, 'YahooProvider', ?, 'MAPPED', 'UNKNOWN', ?)
                    ON CONFLICT(instrument_id, provider) DO UPDATE SET
                        provider_identifier=excluded.provider_identifier,
                        mapping_status='MAPPED', checked_at=excluded.checked_at
                    """,
                    (instrument_id, record.provider_identifier, started),
                )
                active_ids.add(instrument_id)

            for old, new, effective_at in symbol_changes:
                if old in current_symbols:
                    continue
                target = connection.execute(
                    """
                    SELECT instrument_id FROM scanner_instruments
                    WHERE exchange='NSE' AND exchange_symbol=? AND is_active=1
                    """,
                    (new,),
                ).fetchone()
                if target is not None:
                    connection.execute(
                        """
                        INSERT OR REPLACE INTO scanner_instrument_aliases(
                            exchange, alias_symbol, instrument_id,
                            effective_at, source
                        ) VALUES ('NSE', ?, ?, ?, ?)
                        """,
                        (old, target["instrument_id"], effective_at, source),
                    )

            previous_ids = {
                str(row[0])
                for row in connection.execute(
                    """
                    SELECT instrument_id FROM scanner_universe_memberships
                    WHERE universe=?
                    """,
                    (universe,),
                )
            }
            stale_ids = previous_ids - active_ids
            if stale_ids:
                connection.executemany(
                    """
                    UPDATE scanner_instruments SET is_active=0
                    WHERE instrument_id=? AND NOT EXISTS (
                        SELECT 1 FROM scanner_universe_memberships
                        WHERE instrument_id=? AND universe<>?
                    )
                    """,
                    ((item, item, universe) for item in stale_ids),
                )
            connection.execute(
                "DELETE FROM scanner_universe_memberships WHERE universe=?",
                (universe,),
            )
            connection.executemany(
                """
                INSERT INTO scanner_universe_memberships(
                    universe, instrument_id, source, source_updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    (universe, item, source, started)
                    for item in sorted(active_ids)
                ),
            )
            connection.execute(
                """
                UPDATE scanner_timeframe_materializations
                SET state='STALE', updated_at=?
                WHERE universe=? AND state='READY'
                """,
                (started, universe),
            )
            completed = datetime.now(UTC).isoformat()
            connection.execute(
                """
                INSERT INTO scanner_instrument_sync_runs(
                    universe, source, source_checksum, source_count,
                    imported_count, active_count, inactive_count, status,
                    started_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'COMPLETE', ?, ?)
                """,
                (
                    universe,
                    source,
                    source_checksum,
                    len(records),
                    len(records),
                    len(active_ids),
                    len(stale_ids),
                    started,
                    completed,
                ),
            )
            connection.commit()
        return {
            "universe": universe,
            "scope": scope,
            "source": source,
            "source_count": len(records),
            "active_count": len(active_ids),
            "inactive_count": len(stale_ids),
            "series": {
                series: sum(item.series == series for item in records)
                for series in sorted(allowed_series)
            },
            "checksum": source_checksum,
            "completed_at": completed,
        }

    def synchronize_from_nse(self) -> dict[str, object]:
        """Publish authoritative NSE Main and SME masters plus their union."""

        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
        )
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=retry))
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/128.0 Safari/537.36"
            ),
            "Accept": "text/csv,*/*;q=0.8",
            "Referer": "https://www.nseindia.com/",
            "Connection": "close",
        })
        equity = session.get(NSE_MAIN_EQUITY_SOURCE, timeout=60)
        equity.raise_for_status()
        sme = session.get(NSE_SME_EQUITY_SOURCE, timeout=60)
        sme.raise_for_status()
        changes = session.get(NSE_SYMBOL_CHANGE_SOURCE, timeout=60)
        changes.raise_for_status()
        main_result = self.synchronize(
            self.parse_main_equity(equity.content),
            source=NSE_MAIN_EQUITY_SOURCE,
            source_checksum=hashlib.sha256(equity.content).hexdigest(),
            symbol_changes=self.parse_symbol_changes(changes.content),
        )
        sme_records = self.parse_sme_equity(sme.content)
        sme_result = self._synchronize_universe(
            sme_records,
            universe=NSE_SME_EQUITY_UNIVERSE,
            instrument_type="SME_EQUITY",
            scope="NSE SME Equity (SM, ST, SZ)",
            allowed_series=NSE_SME_EQUITY_SERIES,
            source=NSE_SME_EQUITY_SOURCE,
            source_checksum=hashlib.sha256(sme.content).hexdigest(),
        )
        aggregate = self._publish_supported_indian_equity_union()
        return {
            "universe": ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE,
            "scope": "All provider-addressable Indian equity",
            "active_count": aggregate["active_count"],
            "main": main_result,
            "sme": sme_result,
            "aggregate": aggregate,
        }

    def _publish_supported_indian_equity_union(self) -> dict[str, object]:
        """Publish the verified exchange masters without inventing BSE rows."""

        now = datetime.now(UTC).isoformat()
        source = f"{NSE_MAIN_EQUITY_SOURCE}|{NSE_SME_EQUITY_SOURCE}"
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            rows = connection.execute(
                """
                SELECT DISTINCT instrument_id
                FROM scanner_universe_memberships
                WHERE universe IN (?, ?)
                """,
                (NSE_MAIN_EQUITY_UNIVERSE, NSE_SME_EQUITY_UNIVERSE),
            ).fetchall()
            instrument_ids = sorted(str(row[0]) for row in rows)
            connection.execute(
                "DELETE FROM scanner_universe_memberships WHERE universe=?",
                (ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE,),
            )
            connection.executemany(
                """
                INSERT INTO scanner_universe_memberships(
                    universe, instrument_id, source, source_updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    (ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE, item, source, now)
                    for item in instrument_ids
                ),
            )
            connection.execute(
                """
                UPDATE scanner_timeframe_materializations
                SET state='STALE', updated_at=?
                WHERE universe=? AND state='READY'
                """,
                (now, ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE),
            )
            checksum = hashlib.sha256(
                "\n".join(instrument_ids).encode("utf-8")
            ).hexdigest()
            connection.execute(
                """
                INSERT INTO scanner_instrument_sync_runs(
                    universe, source, source_checksum, source_count,
                    imported_count, active_count, inactive_count, status,
                    started_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, 0, 'COMPLETE', ?, ?)
                """,
                (
                    ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE, source, checksum,
                    len(instrument_ids), len(instrument_ids), len(instrument_ids),
                    now, now,
                ),
            )
            connection.commit()
        return {
            "universe": ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE,
            "active_count": len(instrument_ids),
            "checksum": checksum,
            "completed_at": now,
        }

    def _try_claim_sync(self) -> bool:
        """Claim the cross-process synchronization lease if it is available."""

        now = datetime.now(UTC)
        lease_expires = (now + _SYNC_LEASE_DURATION).isoformat()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT status, lease_expires_at
                FROM scanner_instrument_sync_state WHERE universe=?
                """,
                (NSE_MAIN_EQUITY_UNIVERSE,),
            ).fetchone()
            if row is not None and row["status"] == "RUNNING":
                raw_expiry = row["lease_expires_at"]
                if raw_expiry and datetime.fromisoformat(str(raw_expiry)) > now:
                    connection.rollback()
                    return False
            connection.execute(
                """
                INSERT INTO scanner_instrument_sync_state(
                    universe, status, lease_expires_at, last_attempt_at,
                    error_message
                ) VALUES (?, 'RUNNING', ?, ?, NULL)
                ON CONFLICT(universe) DO UPDATE SET
                    status='RUNNING',
                    lease_expires_at=excluded.lease_expires_at,
                    last_attempt_at=excluded.last_attempt_at,
                    error_message=NULL
                """,
                (NSE_MAIN_EQUITY_UNIVERSE, lease_expires, now.isoformat()),
            )
            connection.commit()
        return True

    def _finish_sync_claim(self, *, error_message: str | None = None) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                UPDATE scanner_instrument_sync_state
                SET status=?, lease_expires_at=NULL, error_message=?
                WHERE universe=?
                """,
                (
                    "FAILED" if error_message else "COMPLETE",
                    error_message,
                    NSE_MAIN_EQUITY_UNIVERSE,
                ),
            )

    def synchronize_if_stale(self) -> dict[str, object]:
        """Refresh a stale master without risking the last-known-good membership."""

        if not self.sync_is_stale():
            latest = self.latest_sync()
            return {"status": "CURRENT", "latest_sync": latest}
        if not self._try_claim_sync():
            return {"status": "ALREADY_RUNNING"}
        try:
            result = self.synchronize_from_nse()
        except Exception as error:
            self._finish_sync_claim(error_message=str(error)[:500])
            raise
        self._finish_sync_claim()
        return {"status": "SYNCHRONIZED", **result}

    def coverage_capabilities(self) -> tuple[dict[str, object], ...]:
        """Describe only verified coverage; unavailable scopes remain explicit."""

        latest = self.latest_sync(NSE_MAIN_EQUITY_UNIVERSE)
        active_count = len(self.active_symbols(NSE_MAIN_EQUITY_UNIVERSE))
        sme_latest = self.latest_sync(NSE_SME_EQUITY_UNIVERSE)
        sme_count = len(self.active_symbols(NSE_SME_EQUITY_UNIVERSE))
        aggregate_count = len(
            self.active_symbols(ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE)
        )
        aggregate_provider = self.provider_coverage_summary(
            ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE
        )
        return (
            {
                "id": ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE,
                "display_name": "All Supported Indian Equity",
                "exchange": "NSE",
                "security_scope": "NSE Main and NSE SME; BSE unavailable",
                "state": (
                    "READY"
                    if aggregate_count
                    and aggregate_provider["available"] == aggregate_count
                    else "BOOTSTRAPPING"
                    if aggregate_count
                    else "UNAVAILABLE"
                ),
                "instrument_count": aggregate_count,
                "provider_coverage": aggregate_provider,
                "source": f"{NSE_MAIN_EQUITY_SOURCE}|{NSE_SME_EQUITY_SOURCE}",
                "source_updated_at": (
                    self.latest_sync(ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE) or {}
                ).get("completed_at"),
            },
            {
                "id": NSE_MAIN_EQUITY_UNIVERSE,
                "display_name": "NSE Main Equity",
                "exchange": "NSE",
                "security_scope": "EQ, BE and BZ series",
                "state": "READY" if active_count else "UNAVAILABLE",
                "instrument_count": active_count,
                "source": NSE_MAIN_EQUITY_SOURCE,
                "source_updated_at": latest["completed_at"] if latest else None,
            },
            {
                "id": "nse_sme",
                "display_name": "NSE SME",
                "exchange": "NSE",
                "security_scope": "SME securities",
                "state": "READY" if sme_count else "UNAVAILABLE",
                "instrument_count": sme_count,
                "source": NSE_SME_EQUITY_SOURCE,
                "source_updated_at": sme_latest["completed_at"] if sme_latest else None,
            },
            {
                "id": "nse_etf",
                "display_name": "NSE ETFs",
                "exchange": "NSE",
                "security_scope": "Exchange-traded funds",
                "state": "PROVIDER_DEPENDENT",
                "instrument_count": 0,
                "reason": "ETF membership and provider coverage are not validated.",
            },
            {
                "id": "bse_main",
                "display_name": "BSE Main Equity",
                "exchange": "BSE",
                "security_scope": "Main-board equities",
                "state": "PROVIDER_DEPENDENT",
                "instrument_count": 0,
                "reason": "No validated BSE master/provider mapping is configured.",
            },
            {
                "id": "bse_sme",
                "display_name": "BSE SME",
                "exchange": "BSE",
                "security_scope": "SME securities",
                "state": "UNAVAILABLE",
                "instrument_count": 0,
                "reason": "No validated BSE SME source is configured.",
            },
            {
                "id": "bse_etf",
                "display_name": "BSE ETFs",
                "exchange": "BSE",
                "security_scope": "Exchange-traded funds",
                "state": "PROVIDER_DEPENDENT",
                "instrument_count": 0,
                "reason": "ETF membership and provider coverage are not validated.",
            },
        )

    def provider_coverage_summary(self, universe: str) -> dict[str, int]:
        """Return verified provider-data states for one universe membership."""

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT COALESCE(c.data_status, 'UNMAPPED') status, COUNT(*) count
                FROM scanner_universe_memberships m
                JOIN scanner_instruments i USING(instrument_id)
                LEFT JOIN scanner_provider_capabilities c
                  ON c.instrument_id=i.instrument_id AND c.provider='YahooProvider'
                WHERE m.universe=? AND i.is_active=1
                GROUP BY COALESCE(c.data_status, 'UNMAPPED')
                """,
                (universe,),
            ).fetchall()
        counts = {str(row["status"]): int(row["count"]) for row in rows}
        return {
            "available": counts.get("AVAILABLE", 0),
            "unavailable": counts.get("UNAVAILABLE", 0),
            "unchecked": counts.get("UNKNOWN", 0),
            "unmapped": counts.get("UNMAPPED", 0),
        }

    def has_current_master(
        self, universe: str = NSE_MAIN_EQUITY_UNIVERSE,
    ) -> bool:
        with self._connection() as connection:
            return connection.execute(
                """
                SELECT 1 FROM scanner_instrument_sync_runs
                WHERE universe=? AND status='COMPLETE' LIMIT 1
                """,
                (universe,),
            ).fetchone() is not None

    def active_symbols(
        self, universe: str = NSE_MAIN_EQUITY_UNIVERSE,
    ) -> list[str]:
        with self._connection() as connection:
            return [
                str(row[0])
                for row in connection.execute(
                    """
                    SELECT i.exchange_symbol
                    FROM scanner_universe_memberships m
                    JOIN scanner_instruments i USING(instrument_id)
                    WHERE m.universe=? AND i.exchange='NSE' AND i.is_active=1
                    ORDER BY i.exchange_symbol
                    """,
                    (universe,),
                )
            ]

    def search(self, query: str, limit: int = 10) -> list[dict[str, object]]:
        normalized = query.strip().upper()
        if not normalized:
            return []
        pattern = f"%{normalized}%"
        prefix = f"{normalized}%"
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT i.instrument_id, i.exchange, i.exchange_symbol,
                       i.display_symbol, i.instrument_name, i.isin, i.series,
                       i.is_active, i.provider_identifier,
                       CASE
                         WHEN i.exchange_symbol=? THEN 0
                         WHEN a.alias_symbol=? THEN 1
                         WHEN i.exchange_symbol LIKE ? THEN 2
                         WHEN i.instrument_name LIKE ? THEN 3
                         ELSE 4
                       END AS relevance
                FROM scanner_instruments i
                LEFT JOIN scanner_instrument_aliases a
                  ON a.instrument_id=i.instrument_id
                WHERE i.exchange='NSE' AND i.is_active=1
                  AND (i.exchange_symbol LIKE ? OR upper(i.instrument_name) LIKE ?
                       OR a.alias_symbol LIKE ? OR i.isin LIKE ?)
                ORDER BY relevance, i.exchange_symbol
                LIMIT ?
                """,
                (
                    normalized,
                    normalized,
                    prefix,
                    prefix,
                    pattern,
                    pattern,
                    pattern,
                    pattern,
                    limit,
                ),
            ).fetchall()
        return [dict(row) for row in rows]

    def latest_sync(
        self, universe: str = NSE_MAIN_EQUITY_UNIVERSE,
    ) -> dict[str, object] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT * FROM scanner_instrument_sync_runs
                WHERE universe=? AND status='COMPLETE'
                ORDER BY sync_id DESC LIMIT 1
                """,
                (universe,),
            ).fetchone()
        return dict(row) if row is not None else None

    def sync_is_stale(self, max_age: timedelta = timedelta(days=1)) -> bool:
        latest = self.latest_sync(ALL_SUPPORTED_INDIAN_EQUITY_UNIVERSE)
        if latest is None:
            return True
        completed = datetime.fromisoformat(str(latest["completed_at"]))
        return datetime.now(UTC) - completed > max_age


def start_instrument_master_synchronization(
    service: InstrumentMasterService | None = None,
) -> Future[dict[str, object]]:
    """Start one non-blocking synchronization task per application process."""

    global _sync_future
    selected = service or InstrumentMasterService()
    with _sync_future_lock:
        if _sync_future is None or _sync_future.done():
            _sync_future = _sync_executor.submit(selected.synchronize_if_stale)
        return _sync_future
