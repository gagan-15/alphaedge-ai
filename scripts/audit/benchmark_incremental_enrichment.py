"""Read-only worker benchmark for existing frozen Dhan enrichment engines."""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor

from backend.services.market_data.dhan_dashboard_enrichment_service import (
    _enrich_affected_worker,
)
from backend.services.market_data.dhan_shadow_store import DhanShadowStore
from scripts.audit.benchmark_incremental_eod import COHORT, _cohort


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeframe", default="1D")
    args = parser.parse_args()
    identities = _cohort(args.limit, args.timeframe)
    path = str(DhanShadowStore().path)
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(
            _enrich_affected_worker,
            [path] * len(identities), [COHORT] * len(identities),
            [args.timeframe] * len(identities), identities, chunksize=4,
        ))
    elapsed = time.perf_counter() - started
    print(json.dumps({
        "workers": args.workers, "instruments": len(results),
        "timeframe": args.timeframe,
        "elapsed_seconds": round(elapsed, 3),
        "instruments_per_minute": round(len(results) / elapsed * 60, 2),
        "rows": sum(len(item[2]) for item in results),
        "failures": [item[0] for item in results if item[1] != "COMPLETE"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
