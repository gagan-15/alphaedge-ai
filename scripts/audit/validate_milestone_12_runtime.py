"""Provider-backed Milestone 12 runtime validation helper."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import json
import os
import sqlite3
import sys
import tracemalloc
import threading
from pathlib import Path
from time import perf_counter, process_time, sleep

try:
    import psutil
except ImportError:  # optional operational dependency
    psutil = None

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.api.app import app  # noqa: E402
from backend.core.logger import logger  # noqa: E402


class _ProcessMemoryCounters(ctypes.Structure):
    """Windows PROCESS_MEMORY_COUNTERS used when psutil is unavailable."""

    _fields_ = [
        ("cb", wintypes.DWORD),
        ("page_fault_count", wintypes.DWORD),
        ("peak_working_set_size", ctypes.c_size_t),
        ("working_set_size", ctypes.c_size_t),
        ("quota_peak_paged_pool_usage", ctypes.c_size_t),
        ("quota_paged_pool_usage", ctypes.c_size_t),
        ("quota_peak_non_paged_pool_usage", ctypes.c_size_t),
        ("quota_non_paged_pool_usage", ctypes.c_size_t),
        ("pagefile_usage", ctypes.c_size_t),
        ("peak_pagefile_usage", ctypes.c_size_t),
    ]


def _native_windows_memory() -> tuple[int, int] | None:
    if os.name != "nt":
        return None
    counters = _ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(_ProcessMemoryCounters),
        wintypes.DWORD,
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    current = kernel32.GetCurrentProcess()
    if not psapi.GetProcessMemoryInfo(
        current, ctypes.byref(counters), counters.cb
    ):
        return None
    return counters.working_set_size, counters.peak_working_set_size


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", default="nifty50")
    parser.add_argument("--timeframe", default="DAILY")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--force-stale", action="store_true")
    parser.add_argument("--measure-memory", action="store_true")
    args = parser.parse_args()
    # Canonical engines are intentionally verbose in development. Runtime
    # benchmarks suppress informational logs so console I/O is not measured as
    # scanner computation.
    logger.setLevel("WARNING")
    path = Path("backend/data/scanner/alphaedge-scanner.sqlite3")
    if args.force_stale and path.exists():
        with sqlite3.connect(path) as connection:
            connection.execute(
                """
                UPDATE scanner_snapshots SET completed_at=?
                WHERE universe=? AND timeframe=? AND status='COMPLETE'
                """,
                ("2020-01-01T00:00:00+00:00", args.universe, args.timeframe),
            )
    with sqlite3.connect(path) as connection:
        before_merge = connection.execute(
            """
            SELECT COALESCE(SUM(inserted), 0), COALESCE(SUM(updated), 0),
                   COALESCE(SUM(unchanged), 0), COALESCE(SUM(rejected), 0)
            FROM scanner_candle_merge_audit
            """
        ).fetchone()
    if args.measure_memory:
        tracemalloc.start()
    cpu_started = process_time()
    process = psutil.Process() if psutil else None
    native_baseline = _native_windows_memory()
    baseline_rss = (
        process.memory_info().rss
        if process
        else native_baseline[0] if native_baseline else 0
    )
    peak_rss = baseline_rss
    stop_sampling = threading.Event()

    def sample_resources() -> None:
        nonlocal peak_rss
        while not stop_sampling.wait(0.25):
            if process:
                peak_rss = max(peak_rss, process.memory_info().rss)
            else:
                native = _native_windows_memory()
                if native:
                    peak_rss = max(peak_rss, native[0], native[1])

    sampler = threading.Thread(target=sample_resources, daemon=True)
    sampler.start()
    client = TestClient(app)
    started = perf_counter()
    response = client.get(
        "/scanner/zones",
        params={"universe": args.universe, "timeframe": args.timeframe},
    )
    first_latency = perf_counter() - started
    response.raise_for_status()
    payload = response.json()
    deadline = perf_counter() + args.timeout
    while payload["status"] != "completed" and perf_counter() < deadline:
        sleep(2)
        response = client.get(
            "/scanner/zones",
            params={"universe": args.universe, "timeframe": args.timeframe},
        )
        response.raise_for_status()
        payload = response.json()
    query_started = perf_counter()
    query = client.get(
        "/scanner/persisted-zones",
        params={
            "universe": args.universe,
            "timeframe": args.timeframe,
            "page_size": 3,
            "sort": "zone_quality",
            "descending": True,
        },
    )
    query_latency = perf_counter() - query_started
    query.raise_for_status()
    with sqlite3.connect(path) as connection:
        candle_count = connection.execute(
            "SELECT COUNT(*) FROM scanner_candles"
        ).fetchone()[0]
        quality = connection.execute(
            """
            SELECT data_quality_state, COUNT(*) FROM scanner_candles
            GROUP BY data_quality_state
            """
        ).fetchall()
        jobs = connection.execute(
            "SELECT status, COUNT(*) FROM scanner_jobs GROUP BY status"
        ).fetchall()
        after_merge = connection.execute(
            """
            SELECT COALESCE(SUM(inserted), 0), COALESCE(SUM(updated), 0),
                   COALESCE(SUM(unchanged), 0), COALESCE(SUM(rejected), 0)
            FROM scanner_candle_merge_audit
            """
        ).fetchone()
        stored_payload = connection.execute(
            """
            SELECT payload_json FROM scanner_snapshots
            WHERE universe=? AND timeframe=? AND status='COMPLETE'
            ORDER BY snapshot_id DESC LIMIT 1
            """,
            (args.universe, args.timeframe),
        ).fetchone()
    peak_memory = 0
    if args.measure_memory:
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    stop_sampling.set()
    sampler.join(timeout=1)
    native_final = _native_windows_memory()
    final_rss = (
        process.memory_info().rss
        if process
        else native_final[0] if native_final else 0
    )
    if native_final:
        peak_rss = max(peak_rss, native_final[1])
    elapsed = perf_counter() - started
    cpu_seconds = process_time() - cpu_started
    print(
        {
            "initial_read_ms": round(first_latency * 1000, 3),
            "final_status": payload["status"],
            "scanned": payload["total_scanned"],
            "zones": payload["total_zones"],
            "failed": payload["failed_symbols"],
            "persisted_query_ms": round(query_latency * 1000, 3),
            "persisted_total": query.json()["total"],
            "exact_payload_parity": (
                json.loads(stored_payload[0]) == payload
                if stored_payload and stored_payload[0]
                else False
            ),
            "candles": candle_count,
            "data_quality": quality,
            "jobs": jobs,
            "merge_delta": {
                key: int(after_merge[index] - before_merge[index])
                for index, key in enumerate(
                    ("inserted", "updated", "unchanged", "rejected")
                )
            },
            "process_cpu_seconds": round(cpu_seconds, 3),
            "cpu_utilization_one_core_percent": (
                round(cpu_seconds / elapsed * 100, 2) if elapsed else 0.0
            ),
            "cpu_utilization_host_percent": (
                round(cpu_seconds / elapsed / (os.cpu_count() or 1) * 100, 2)
                if elapsed else 0.0
            ),
            "active_threads": threading.active_count(),
            "baseline_process_memory_mb": (
                round(baseline_rss / 1024 / 1024, 2) if baseline_rss else None
            ),
            "peak_process_memory_mb": (
                round(peak_rss / 1024 / 1024, 2) if peak_rss else None
            ),
            "final_process_memory_mb": (
                round(final_rss / 1024 / 1024, 2) if final_rss else None
            ),
            "python_peak_memory_mb": (
                round(peak_memory / 1024 / 1024, 2)
                if args.measure_memory
                else None
            ),
        }
    )


if __name__ == "__main__":
    main()
