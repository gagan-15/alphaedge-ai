"""Read-only benchmark/parity gate for dependency-aware Dhan EOD formation."""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from concurrent.futures import ProcessPoolExecutor

from backend.core.logger import logger
from backend.services.market_data.dhan_shadow_store import DhanShadowStore
from backend.services.market_data.incremental_canonical_service import (
    IncrementalCanonicalService,
)

COHORT = "dhan_all_supported_indian_equity"
_STORE: DhanShadowStore | None = None
_SERVICE: IncrementalCanonicalService | None = None


def _one(instrument_id: str, timeframe: str = "1D") -> tuple[str, bool, float, int]:
    global _STORE, _SERVICE
    logger.setLevel(logging.ERROR)
    if _STORE is None:
        _STORE = DhanShadowStore()
    if _SERVICE is None:
        _SERVICE = IncrementalCanonicalService()
    store = _STORE
    data = store.load(instrument_id, timeframe)
    rows = store.active_structured_zone_payloads_for_instrument(
        COHORT, timeframe, instrument_id,
    )
    started = time.perf_counter()
    result = _SERVICE.refresh_validated(
        data, rows, data.index[-1], append_only=True,
    )
    elapsed = time.perf_counter() - started
    expected = [json.loads(str(row["payload"])) for row in rows]
    actual = [store._structured_payload(zone) for zone in result.zones]
    normalized_expected = sorted(json.dumps(item, sort_keys=True) for item in expected)
    normalized_actual = sorted(json.dumps(item, sort_keys=True) for item in actual)
    return (
        instrument_id, normalized_actual == normalized_expected,
        elapsed, len(result.zones),
    )


def _cohort(limit: int, timeframe: str = "1D") -> list[str]:
    store = DhanShadowStore()
    with store.connection() as connection:
        rows = connection.execute(
            """SELECT c.instrument_id,
                      (SELECT COUNT(*) FROM dhan_shadow_zones z
                       WHERE z.cohort=c.cohort AND z.instrument_id=c.instrument_id
                         AND z.timeframe=?) AS zones,
                      (SELECT COUNT(*) FROM dhan_shadow_candles k
                       WHERE k.instrument_id=c.instrument_id
                         AND k.timeframe=?) AS candles
               FROM dhan_canonical_checkpoints c
               WHERE c.cohort=? AND c.timeframe=? AND c.status='COMPLETE'
                 AND (SELECT COUNT(*) FROM dhan_shadow_candles k
                      WHERE k.instrument_id=c.instrument_id
                        AND k.timeframe=?)>=3
               ORDER BY c.instrument_id
               LIMIT ?""", (
                timeframe, timeframe, COHORT, timeframe, timeframe, limit,
            ),
        ).fetchall()
    identities = [str(row["instrument_id"]) for row in rows]
    if timeframe == "1D" and "NSE:3761" not in identities and identities:
        identities[-1] = "NSE:3761"
    return identities


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--timeframe", default="1D")
    args = parser.parse_args()
    identities = _cohort(args.limit, args.timeframe)
    started = time.perf_counter()
    if args.workers == 1:
        results = [_one(identity, args.timeframe) for identity in identities]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(
                pool.map(_one, identities, [args.timeframe] * len(identities), chunksize=4)
            )
    elapsed = time.perf_counter() - started
    print(json.dumps({
        "workers": args.workers,
        "timeframe": args.timeframe,
        "instruments": len(results),
        "elapsed_seconds": round(elapsed, 3),
        "instruments_per_minute": round(len(results) / elapsed * 60, 2),
        "parity_passed": sum(item[1] for item in results),
        "parity_failed": sum(not item[1] for item in results),
        "parity_failure_instruments": [item[0] for item in results if not item[1]],
        "calculation_seconds": round(sum(item[2] for item in results), 3),
        "pid": os.getpid(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
