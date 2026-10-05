"""Materialize a Dhan Dashboard-result snapshot from persisted canonical zones.

This operational runner never downloads candles or invokes zone detection.
"""

from __future__ import annotations

import argparse

from backend.services.market_data.dhan_dashboard_enrichment_service import (
    DhanDashboardEnrichmentService,
)
from backend.services.market_data.dhan_shadow_service import DhanShadowService
from backend.services.market_data.dhan_shadow_store import DhanShadowStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeframe", required=True, choices=("1D", "1W", "1M", "3M", "6M", "1Y"))
    parser.add_argument("--cohort", default="dhan_all_supported_indian_equity")
    parser.add_argument("--repair-legacy", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    store = DhanShadowStore()
    if args.repair_legacy:
        print(DhanShadowService(store=store).rebuild_structured_evidence(
            args.timeframe, args.cohort, args.workers
        ))
    result = DhanDashboardEnrichmentService(store).materialize(args.timeframe, args.cohort)
    print(result)


if __name__ == "__main__":
    main()
