#!/usr/bin/env python
# flake8: noqa: E402
"""Repeatable local latency benchmark for the Milestone 10B read model."""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.historical_evidence.constants import HISTORICAL_EVIDENCE_VERSION
from backend.historical_evidence.service import HistoricalEvidenceService


def benchmark(call, iterations: int = 50) -> dict[str, float]:
    samples = []
    for _ in range(iterations):
        started = perf_counter()
        call()
        samples.append((perf_counter() - started) * 1000)
    ordered = sorted(samples)
    return {
        "median_ms": round(statistics.median(samples), 3),
        "p95_ms": round(ordered[int(iterations * 0.95) - 1], 3),
        "max_ms": round(max(samples), 3),
    }


def main() -> None:
    service = HistoricalEvidenceService()
    version = HISTORICAL_EVIDENCE_VERSION
    unfiltered = service.filters()
    filtered = service.filters(
        timeframe="1D", zone_type="DEMAND", pattern="DBR",
        trade_confidence_label="MODERATE",
    )
    cases = {
        "metadata": lambda: service.metadata(version),
        "unfiltered_summary": lambda: service.summary(version, unfiltered),
        "filtered_summary": lambda: service.summary(version, filtered),
        "paginated_zones": lambda: service.zones(
            version, filtered, page=1, page_size=50,
            sort_by="formation_timestamp", sort_direction="desc",
        ),
    }
    print(json.dumps({name: benchmark(call) for name, call in cases.items()}, indent=2))


if __name__ == "__main__":
    main()
