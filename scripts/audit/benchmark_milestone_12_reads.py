"""Measure user-facing read latency while a scanner refresh is active."""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from time import perf_counter

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.api.app import app  # noqa: E402


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, int((len(ordered) - 1) * fraction))
    return ordered[index]


def main() -> None:
    client = TestClient(app)
    endpoints = {
        "capabilities": ("/scanner/capabilities", {}),
        "allnse_dashboard": (
            "/scanner/zones",
            {
                "universe": "allnse",
                "timeframe": "DAILY",
                "include_results": False,
            },
        ),
        "allnse_page": (
            "/scanner/persisted-zones",
            {"universe": "allnse", "timeframe": "DAILY", "page_size": 14},
        ),
        "allnse_filtered_sorted_page": (
            "/scanner/persisted-zones",
            {
                "universe": "allnse",
                "timeframe": "DAILY",
                "zone_type": "DEMAND",
                "min_zone_quality": 40,
                "sort": "zone_quality",
                "descending": True,
                "page_size": 3,
            },
        ),
        "nse500_universe_switch": (
            "/scanner/persisted-zones",
            {"universe": "nse500", "timeframe": "DAILY", "page_size": 14},
        ),
        "nifty50_weekly_switch": (
            "/scanner/persisted-zones",
            {"universe": "nifty50", "timeframe": "WEEKLY", "page_size": 14},
        ),
        "historical_metadata": ("/historical-evidence/metadata", {}),
    }
    report: dict[str, object] = {}
    for name, (path, params) in endpoints.items():
        timings: list[float] = []
        failures = 0
        for _ in range(20):
            started = perf_counter()
            response = client.get(path, params=params)
            timings.append((perf_counter() - started) * 1000)
            if response.status_code != 200:
                failures += 1
        report[name] = {
            "cold_first_ms": round(timings[0], 3),
            "warm_p50_ms": round(statistics.median(timings[1:]), 3),
            "warm_p95_ms": round(percentile(timings[1:], 0.95), 3),
            "warm_max_ms": round(max(timings[1:]), 3),
            "failures": failures,
        }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
