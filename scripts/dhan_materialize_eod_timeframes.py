"""Build Dhan higher EOD frames from persisted Daily candles only.

This runner deliberately has no Dhan provider instance: it cannot download
market data or call Yahoo.  It resumes canonical checkpoints and materializes
the requested frames sequentially so SQLite persistence remains controlled.
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
    parser.add_argument("--timeframes", nargs="+", choices=("3M", "6M", "1Y"), required=True)
    parser.add_argument("--cohort", default="dhan_all_supported_indian_equity")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    store = DhanShadowStore()
    service = DhanShadowService(store=store)
    enrichment = DhanDashboardEnrichmentService(store)
    for timeframe in args.timeframes:
        print({"timeframe": timeframe, "canonical": service.materialize_eod_snapshot_parallel(
            timeframe, args.cohort, args.workers,
        )}, flush=True)
        print({"timeframe": timeframe, "dashboard": enrichment.materialize(
            timeframe, args.cohort,
        )}, flush=True)


if __name__ == "__main__":
    main()
