"""Read-only operational snapshot for Milestone 12 scanner progress."""

from __future__ import annotations

import sqlite3
import json
from collections import Counter
from pathlib import Path


path = Path("backend/data/scanner/alphaedge-scanner.sqlite3")
with sqlite3.connect(path) as connection:
    print("database_bytes", path.stat().st_size)
    print(
        "jobs",
        connection.execute(
            """
            SELECT job_id, universe, timeframe, status, processed_instruments,
                   total_instruments, failed_instruments, started_at,
                   heartbeat_at, lease_expires_at, error_message
            FROM scanner_jobs ORDER BY job_id DESC LIMIT 5
            """
        ).fetchall(),
    )
    print(
        "checkpoints",
        connection.execute(
            """
            SELECT timeframe, status, COUNT(*)
            FROM scanner_symbol_checkpoints
            GROUP BY timeframe, status
            """
        ).fetchall(),
    )
    print(
        "checkpoint_errors",
        connection.execute(
            """
            SELECT SUBSTR(error_message, 1, 180), COUNT(*)
            FROM scanner_symbol_checkpoints WHERE status!='COMPLETE'
            GROUP BY SUBSTR(error_message, 1, 180)
            ORDER BY COUNT(*) DESC LIMIT 10
            """
        ).fetchall(),
    )
    print(
        "allnse_snapshots",
        connection.execute(
            """
            SELECT snapshot_id, status, total_symbols, successful_instruments,
                   failed_instruments, result_count, started_at, completed_at,
                   error_message
            FROM scanner_snapshots WHERE universe='allnse'
            ORDER BY snapshot_id DESC LIMIT 5
            """
        ).fetchall(),
    )
    print(
        "candles",
        connection.execute("SELECT COUNT(*) FROM scanner_candles").fetchone()[0],
    )
    print(
        "result_rows",
        connection.execute("SELECT COUNT(*) FROM scanner_result_rows").fetchone()[0],
    )
    print(
        "ready_timeframes",
        connection.execute(
            """
            SELECT snapshot_id, universe, timeframe, methodology_version,
                   result_count, completed_at
            FROM scanner_snapshots WHERE status='COMPLETE'
            ORDER BY snapshot_id DESC
            """
        ).fetchall(),
    )
    for timeframe in ("WEEKLY", "MONTHLY"):
        payloads = [
            json.loads(row[0])
            for row in connection.execute(
                """
                SELECT response_json FROM scanner_symbol_checkpoints
                WHERE timeframe=? AND status='COMPLETE'
                """,
                (timeframe,),
            ).fetchall()
        ]
        rejections: Counter[str] = Counter()
        for payload in payloads:
            rejections.update(payload.get("qualification_rejection_counts", {}))
        print(
            f"{timeframe.lower()}_pipeline",
            {
                "checkpoints": len(payloads),
                "canonical_zones": sum(
                    item.get("canonical_zone_count", 0) for item in payloads
                ),
                "formation_qualified": sum(
                    item.get("formation_qualified_count", 0) for item in payloads
                ),
                "dashboard_qualified": sum(
                    item.get("dashboard_qualified_count", 0) for item in payloads
                ),
                "returned_zones": sum(
                    item.get("total_zones", 0) for item in payloads
                ),
                "rejections": dict(rejections),
            },
        )
    latest_start = connection.execute(
        """
        SELECT started_at FROM scanner_jobs
        WHERE universe='allnse' AND timeframe='DAILY' AND status='COMPLETE'
        ORDER BY job_id DESC LIMIT 1
        """
    ).fetchone()[0]
    print(
        "latest_allnse_recalculated_checkpoints",
        connection.execute(
            """
            SELECT COUNT(*) FROM scanner_symbol_checkpoints
            WHERE timeframe='DAILY' AND status='COMPLETE' AND completed_at>=?
            """,
            (latest_start,),
        ).fetchone()[0],
    )
