# flake8: noqa: E402
"""Run a bounded, provider-backed Milestone 11A confirmation study."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.research.entry_confirmation_research import (
    EntryConfirmationResearchEngine,
    summarize_confirmation_observations,
)
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.market_data.timeframe_service import aggregate_timeframe
from backend.services.scanner.universe_service import UniverseService


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    symbols = UniverseService().get_symbols("nse500")[: args.limit]
    records = []
    failures = []
    coverage = {}

    def process(symbol: str):
        service = MarketDataService()
        engine = EntryConfirmationResearchEngine()
        symbol_records = []
        symbol_coverage = {}
        try:
            validated = service.get_stock_data_segments(symbol, "5y", "1d")
            for segment in validated.segments:
                if len(segment) < 20:
                    continue
                for timeframe in ("1D", "1W"):
                    frame = (
                        segment
                        if timeframe == "1D"
                        else aggregate_timeframe(segment, "1W")
                    )
                    if len(frame) < 5:
                        continue
                    rows = engine.replay(frame, symbol=symbol, timeframe=timeframe)
                    symbol_records.extend(rows)
                    symbol_coverage.setdefault(
                        timeframe, {"series": 0, "candles": 0, "interactions": 0}
                    )
                    symbol_coverage[timeframe]["series"] += 1
                    symbol_coverage[timeframe]["candles"] += len(frame)
                    symbol_coverage[timeframe]["interactions"] += len(rows)
            return symbol, symbol_records, symbol_coverage, None
        except Exception as error:
            return (
                symbol,
                [],
                {},
                {
                    "symbol": symbol,
                    "error": type(error).__name__,
                    "message": str(error),
                },
            )

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(process, symbol): symbol for symbol in symbols}
        for number, future in enumerate(as_completed(futures), 1):
            symbol, symbol_records, symbol_coverage, failure = future.result()
            records.extend(symbol_records)
            if failure:
                failures.append(failure)
            for timeframe, values in symbol_coverage.items():
                coverage.setdefault(
                    timeframe, {"series": 0, "candles": 0, "interactions": 0}
                )
                for key, value in values.items():
                    coverage[timeframe][key] += value
            print(
                f"{number}/{len(symbols)} {symbol} interactions={len(records)}",
                flush=True,
            )
    payload = {
        "audit": "MILESTONE_11B_LARGE_SCALE_ENTRY_CONFIRMATION_VALIDATION",
        "production_activation": False,
        "symbols_requested": len(symbols),
        "symbols": symbols,
        "failures": failures,
        "coverage": coverage,
        "records": records,
        "summary": summarize_confirmation_observations(records),
        "limitations": [
            "Frozen Historical Evidence V1 does not retain interaction OHLC candles.",
            "This bounded provider-backed study is not the frozen 37,725-zone dataset.",
            "Intraday and same-TF versus lower-TF evidence are not evaluated by this run.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
