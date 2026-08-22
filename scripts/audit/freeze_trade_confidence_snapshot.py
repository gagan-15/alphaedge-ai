"""Freeze a Pre-Milestone 7E scanner snapshot; never used by production."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.api.scanner import _scan_research_zones


def main() -> None:
    started = perf_counter()
    response = _scan_research_zones("DAILY", "nse500", None)
    payload = response.model_dump(mode="json")
    payload["audit"] = {
        "kind": "PRE_MILESTONE_7E_FROZEN_SAME_ZONE_AUDIT",
        "scan_duration_seconds": round(perf_counter() - started, 3),
        "production_behavior_changed": False,
    }
    target = Path("tests/fixtures/trade_confidence_nse500_daily_snapshot.json")
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "target": str(target),
                "symbols": response.total_symbols,
                "processed": response.processed_symbols,
                "failed": response.failed_symbols,
                "canonical_zones": response.canonical_zone_count,
                "dashboard_zones": response.total_zones,
                "duration_seconds": payload["audit"]["scan_duration_seconds"],
                "trade_confidence": sum(
                    item.trade_confidence is not None for item in response.results
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
