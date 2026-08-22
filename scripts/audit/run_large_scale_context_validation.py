# flake8: noqa: E501
"""Run restartable NSE 500 Daily/Weekly Milestone 9C research replay."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import logging
from pathlib import Path
import sys
from time import perf_counter

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.core.logger import logger  # noqa: E402
from backend.research.large_scale_historical_replay import (  # noqa: E402
    LargeScaleHistoricalReplayEngine,
)
from backend.services.market_data.market_data_service import (  # noqa: E402
    MarketDataService,
)
from backend.services.market_data.timeframe_service import (  # noqa: E402
    aggregate_timeframe,
)
from backend.services.scanner.universe_service import UniverseService  # noqa: E402


START = pd.Timestamp("2021-08-01")
END = pd.Timestamp("2026-08-18")


def _frame(data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    return data if timeframe == "1D" else aggregate_timeframe(data, timeframe)


def _atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    temporary.replace(path)


def _empty_manifest(symbols: list[str], shard: int, count: int) -> dict:
    checksum = hashlib.sha256("\n".join(symbols).encode()).hexdigest()
    return {
        "audit": {
            "name": "MILESTONE_9C_LARGE_SCALE_DAILY_WEEKLY_VALIDATION",
            "production_activation": False,
            "universe": "nse500",
            "universe_checksum": checksum,
            "period_start": str(START.date()),
            "period_end": str(END.date()),
            "shard_index": shard,
            "shard_count": count,
            "complete": False,
        },
        "symbols": {},
    }


def _run_symbol(service: MarketDataService, symbol: str) -> dict:
    started = perf_counter()
    validated = service.get_stock_data_segments(symbol, "5y", "1d")
    engine = LargeScaleHistoricalReplayEngine()
    snapshots = []
    observations = []
    contexts = []
    series = []
    for source_segment in validated.segments:
        index = pd.DatetimeIndex(source_segment.index)
        comparable = index.tz_localize(None) if index.tz is not None else index
        mask = (comparable >= START) & (comparable <= END)
        daily = source_segment.loc[mask].copy()
        if len(daily) < 20:
            continue
        for timeframe, location_tf, trend_tf in (
            ("1D", "1M", "1W"),
            ("1W", "3M", "1M"),
        ):
            execution = _frame(daily, timeframe)
            location = _frame(daily, location_tf)
            trend = _frame(daily, trend_tf)
            if len(execution) < 5:
                continue
            result = engine.replay(
                execution,
                symbol=symbol,
                timeframe=timeframe,
                location=location,
                trend=trend,
            )
            snapshots.extend(result["snapshots"])
            observations.extend(result["observations"])
            contexts.extend(result["contexts"])
            series.append(
                {
                    "timeframe": timeframe,
                    "candles": len(execution),
                    "first": str(execution.index[0]),
                    "last": str(execution.index[-1]),
                    "discovered": result["discovered"],
                    "reconstructed": result["reconstructed"],
                    "skipped": result["skipped"],
                }
            )
    if not series:
        raise ValueError("No valid Daily/Weekly series in the frozen period")
    return {
        "status": "PROCESSED",
        "duration_seconds": round(perf_counter() - started, 3),
        "zero_range_candles": len(validated.zero_range_rows),
        "zero_range_timestamps": [str(item) for item in validated.zero_range_rows],
        "series": series,
        "snapshots": snapshots,
        "observations": observations,
        "contexts": contexts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    all_symbols = UniverseService().get_symbols("nse500")
    symbols = [
        symbol
        for index, symbol in enumerate(all_symbols)
        if index % args.shard_count == args.shard_index
    ]
    if args.limit is not None:
        symbols = symbols[: args.limit]
    payload = (
        json.loads(args.output.read_text(encoding="utf-8"))
        if args.output.exists()
        else _empty_manifest(all_symbols, args.shard_index, args.shard_count)
    )
    expected = _empty_manifest(all_symbols, args.shard_index, args.shard_count)["audit"]
    if payload["audit"]["universe_checksum"] != expected["universe_checksum"]:
        raise ValueError("Checkpoint universe checksum does not match frozen NSE 500")
    service = MarketDataService()
    logger.setLevel(logging.WARNING)
    for number, symbol in enumerate(symbols, 1):
        existing = payload["symbols"].get(symbol)
        if existing and existing.get("status") == "PROCESSED":
            continue
        try:
            payload["symbols"][symbol] = _run_symbol(service, symbol)
        except Exception as error:
            payload["symbols"][symbol] = {
                "status": "FAILED",
                "error": type(error).__name__,
                "message": str(error),
            }
        _atomic_json(args.output, payload)
        done = sum(
            item.get("status") == "PROCESSED"
            for item in payload["symbols"].values()
        )
        failed = sum(
            item.get("status") == "FAILED"
            for item in payload["symbols"].values()
        )
        zones = sum(
            len(item.get("snapshots", ())) for item in payload["symbols"].values()
        )
        print(
            f"shard {args.shard_index}: {number}/{len(symbols)} {symbol} "
            f"processed={done} failed={failed} zones={zones}",
            flush=True,
        )
    payload["audit"]["complete"] = all(
        symbol in payload["symbols"] for symbol in symbols
    )
    payload["summary"] = {
        "requested": len(symbols),
        "processed": sum(
            item.get("status") == "PROCESSED"
            for item in payload["symbols"].values()
        ),
        "failed": sum(
            item.get("status") == "FAILED"
            for item in payload["symbols"].values()
        ),
        "zones": sum(
            len(item.get("snapshots", ())) for item in payload["symbols"].values()
        ),
        "tc_distribution": dict(
            Counter(
                context["trade_confidence"].get("label", "UNAVAILABLE")
                for item in payload["symbols"].values()
                for context in item.get("contexts", ())
            )
        ),
    }
    _atomic_json(args.output, payload)
    print(json.dumps(payload["summary"], indent=2), flush=True)


if __name__ == "__main__":
    main()
