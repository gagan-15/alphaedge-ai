# flake8: noqa: E501
"""Reconstruct Milestone 9B point-in-time ZQ and Trade Confidence."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys
from time import perf_counter

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.config.gtf_workflow_roles import resolve_gtf_workflow  # noqa: E402
from backend.core.logger import logger  # noqa: E402
from backend.engines.demand_supply_engine.zone_detection_engine import (  # noqa: E402
    ZoneDetectionEngine,
)
from backend.research.historical_context_validation import (  # noqa: E402
    HistoricalContextReconstructor,
)
from backend.services.market_data.market_data_service import MarketDataService  # noqa: E402
from backend.services.market_data.timeframe_service import (  # noqa: E402
    INTRADAY_SOURCES,
    aggregate_timeframe,
)


def source_for(timeframe: str) -> tuple[str, str]:
    if timeframe in INTRADAY_SOURCES:
        return INTRADAY_SOURCES[timeframe]
    if timeframe == "1W":
        return "10y", "1wk"
    if timeframe == "1M":
        return "10y", "1mo"
    return "5y", "1d"


def load_segments(service: MarketDataService, symbol: str, timeframe: str):
    period, interval = source_for(timeframe)
    validated = service.get_stock_data_segments(symbol, period, interval)
    result = []
    for segment in validated.segments:
        framed = segment if timeframe in {"15m", "1D", "1W", "1M"} else aggregate_timeframe(segment, timeframe)
        if not framed.empty:
            result.append(framed)
    return result


def segment_at(segments, timestamp):
    target = pd.Timestamp(timestamp)
    for segment in segments:
        index = pd.DatetimeIndex(segment.index)
        comparable = target
        if index.tz is not None and comparable.tzinfo is None:
            comparable = comparable.tz_localize(index.tz)
        elif index.tz is None and comparable.tzinfo is not None:
            comparable = comparable.tz_localize(None)
        if index[0] <= comparable <= index[-1]:
            return segment
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--symbols", default="")
    args = parser.parse_args()
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in args.input]
    snapshots = [row for payload in payloads for row in payload["snapshots"]]
    selected_symbols = {
        item.strip().upper() for item in args.symbols.split(",") if item.strip()
    }
    if selected_symbols:
        snapshots = [
            row for row in snapshots if row["symbol"] in selected_symbols
        ]
    if args.limit is not None:
        snapshots = snapshots[: args.limit]
    service = MarketDataService()
    reconstructor = HistoricalContextReconstructor()
    cache = {}
    detected_cache = {}
    rows = []
    failures = []
    started = perf_counter()
    logger.setLevel(logging.WARNING)
    for number, snapshot in enumerate(snapshots, 1):
        symbol = snapshot["symbol"]
        execution_tf = snapshot["timeframe"]
        workflow = resolve_gtf_workflow(execution_tf)
        needed = {execution_tf, workflow.location, workflow.trend} - {None}
        try:
            for timeframe in needed:
                key = (symbol, timeframe)
                if key not in cache:
                    cache[key] = load_segments(service, symbol, timeframe)
            execution = segment_at(cache[(symbol, execution_tf)], snapshot["planning_timestamp"])
            if execution is None:
                raise ValueError("Execution segment unavailable at planning timestamp")
            execution_key = (symbol, execution_tf, id(execution))
            if execution_key not in detected_cache:
                detected_cache[execution_key] = ZoneDetectionEngine().detect_zones(
                    execution
                )
            location_segments = cache.get((symbol, workflow.location), [])
            trend_segments = cache.get((symbol, workflow.trend), [])
            location = segment_at(location_segments, snapshot["planning_timestamp"])
            trend = segment_at(trend_segments, snapshot["planning_timestamp"])
            rows.append(
                reconstructor.reconstruct(
                    snapshot,
                    execution,
                    location_data=location,
                    trend_data=trend,
                    execution_zones=detected_cache[execution_key],
                )
            )
        except Exception as error:
            failures.append(
                {
                    "zone_id": snapshot["zone_id"],
                    "symbol": symbol,
                    "timeframe": execution_tf,
                    "error": type(error).__name__,
                    "message": str(error),
                }
            )
            rows.append(reconstructor._unavailable(snapshot, type(error).__name__))
        if number % 100 == 0:
            print(f"reconstructed {number}/{len(snapshots)}", flush=True)
    output = {
        "audit": {
            "name": "MILESTONE_9B_HISTORICAL_CONTEXT_RECONSTRUCTION",
            "production_activation": False,
            "duration_seconds": round(perf_counter() - started, 3),
        },
        "dataset": {
            "historical_zones": len(snapshots),
            "source_inputs": [str(path) for path in args.input],
            "cached_symbol_timeframes": len(cache),
        },
        "records": rows,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(json.dumps({**output["dataset"], "failures": len(failures)}, indent=2))


if __name__ == "__main__":
    main()
