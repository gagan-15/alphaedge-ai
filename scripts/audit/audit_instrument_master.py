"""Audit or synchronize the persistent NSE Main Equity instrument master."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.scanner.instrument_master_service import (  # noqa: E402
    InstrumentMasterService,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synchronize", action="store_true")
    args = parser.parse_args()
    service = InstrumentMasterService()
    sync_result = service.synchronize_if_stale() if args.synchronize else None
    with sqlite3.connect(service.path) as connection:
        connection.row_factory = sqlite3.Row
        series = {
            str(row["series"]): int(row["total"])
            for row in connection.execute(
                """
                SELECT series, COUNT(*) AS total FROM scanner_instruments
                WHERE exchange='NSE' AND is_active=1 GROUP BY series
                """
            )
        }
        tmpv = connection.execute(
            """
            SELECT instrument_id, exchange_symbol, instrument_name, isin, series,
                   provider_identifier, is_active
            FROM scanner_instruments WHERE exchange_symbol='TMPV'
            """
        ).fetchone()
        membership_count = connection.execute(
            """
            SELECT COUNT(*) FROM scanner_universe_memberships
            WHERE universe='allnse'
            """
        ).fetchone()[0]
        inactive = [dict(row) for row in connection.execute(
            """
            SELECT exchange_symbol, instrument_name, isin, series
            FROM scanner_instruments WHERE exchange='NSE' AND is_active=0
            ORDER BY exchange_symbol
            """
        )]
        aliases = connection.execute(
            "SELECT COUNT(*) FROM scanner_instrument_aliases"
        ).fetchone()[0]
        provider_states = {
            f"{row['mapping_status']}/{row['data_status']}": int(row["total"])
            for row in connection.execute(
                """
                SELECT mapping_status, data_status, COUNT(*) AS total
                FROM scanner_provider_capabilities
                GROUP BY mapping_status, data_status
                """
            )
        }
        candle_count, candle_instruments = connection.execute(
            """
            SELECT COUNT(*), COUNT(DISTINCT instrument_id)
            FROM scanner_candles
            """
        ).fetchone()
    print(json.dumps({
        "synchronization": sync_result,
        "latest_sync": service.latest_sync(),
        "active_symbols": len(service.active_symbols()),
        "allnse_memberships": membership_count,
        "series": series,
        "inactive_instruments": inactive,
        "symbol_aliases": aliases,
        "provider_states": provider_states,
        "persisted_candles": candle_count,
        "instruments_with_candles": candle_instruments,
        "database_bytes": service.path.stat().st_size,
        "tmpv": dict(tmpv) if tmpv else None,
        "coverage": service.coverage_capabilities(),
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
