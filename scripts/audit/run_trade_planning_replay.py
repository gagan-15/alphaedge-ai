"""Run the approved Milestone 8 historical planning calibration study.

This command is research-only. It does not write scanner caches or alter any
production methodology. JSON contains row-level evidence; Markdown contains a
compact review report.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import json
from pathlib import Path
from statistics import median
import sys
from time import perf_counter
import logging
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.models.trade_planning_replay import (  # noqa: E402
    ReplayEntryPolicy,
    ReplayOutcome,
    ReplayStopPolicy,
)
from backend.research.trade_planning_replay import (  # noqa: E402
    TradePlanningReplayEngine,
)
from backend.services.market_data.market_data_service import (  # noqa: E402
    MarketDataService,
)
from backend.services.market_data.timeframe_service import (  # noqa: E402
    INTRADAY_SOURCES,
    aggregate_timeframe,
)
from backend.core.logger import logger  # noqa: E402

DEFAULT_SYMBOLS = (
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "INFY",
    "ICICIBANK",
    "SBIN",
    "HINDALCO",
    "AUBANK",
    "MAXHEALTH",
    "SUNPHARMA",
    "MARUTI",
    "ITC",
)
TIMEFRAMES = ("15m", "75m", "125m", "1D", "1W")


def source_for(timeframe: str) -> tuple[str, str]:
    if timeframe in INTRADAY_SOURCES:
        return INTRADAY_SOURCES[timeframe]
    return ("5y", "1d")


def timeframe_data(data, timeframe: str):
    if timeframe == "1D":
        return data
    return aggregate_timeframe(data, timeframe)


def rate(count: int, denominator: int) -> float:
    return round(100 * count / denominator, 2) if denominator else 0.0


def comparable_timestamp(value) -> pd.Timestamp:
    """Normalize provider timestamps solely for report-range comparison."""

    timestamp = pd.Timestamp(value)
    return timestamp.tz_localize(None) if timestamp.tzinfo is not None else timestamp


def summarize(observations: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in observations:
        groups[(row["timeframe"], row["entry_policy"], row["stop_policy"])].append(row)
    summary = []
    for key, rows in sorted(groups.items()):
        entered = [row for row in rows if row["entry_index"] is not None]
        decided = [
            row
            for row in entered
            if row["outcome"]
            in {
                ReplayOutcome.TARGET_BEFORE_STOP.value,
                ReplayOutcome.STOP_BEFORE_TARGET.value,
            }
        ]
        targets = sum(
            row["outcome"] == ReplayOutcome.TARGET_BEFORE_STOP.value for row in rows
        )
        stops = sum(
            row["outcome"] == ReplayOutcome.STOP_BEFORE_TARGET.value for row in rows
        )
        rrs = [
            row["structural_risk_reward"]
            for row in rows
            if row["structural_risk_reward"] is not None
        ]
        maes = [row["mae_atr"] for row in entered if row["mae_atr"] is not None]
        mfes = [row["mfe_atr"] for row in entered if row["mfe_atr"] is not None]
        summary.append(
            {
                "timeframe": key[0],
                "entry_policy": key[1],
                "stop_policy": key[2],
                "zones": len(rows),
                "fill_rate_percent": rate(len(entered), len(rows)),
                "target_before_stop_percent": rate(targets, len(decided)),
                "stop_before_target_percent": rate(stops, len(decided)),
                "median_structural_rr": round(median(rrs), 4) if rrs else None,
                "median_mae_atr": round(median(maes), 4) if maes else None,
                "median_mfe_atr": round(median(mfes), 4) if mfes else None,
            }
        )
    return summary


def markdown(payload: dict) -> str:
    dataset = payload["dataset"]
    lines = [
        "# Milestone 8 - Historical Trade Planning Replay",
        "",
        "> Research infrastructure only. Canonical Trade Planning V1 is not active.",
        "",
        "## Dataset",
        "",
        f"- Symbols requested: {dataset['symbols_requested']}",
        f"- Successful symbol/timeframe series: {dataset['series_succeeded']}",
        f"- Failed series: {dataset['series_failed']}",
        f"- Reconstructed canonical zones: {dataset['zones_reconstructed']}",
        f"- Date range: {dataset['date_start']} to {dataset['date_end']}",
        f"- Provider: {dataset['provider']}",
        "- Tick size: unavailable from the current provider contract; "
        "no universal tick was assumed.",
        "",
        "## Coverage",
        "",
        f"- Timeframes: {payload['breakdowns']['timeframes']}",
        f"- Zone types: {payload['breakdowns']['zone_types']}",
        f"- Patterns: {payload['breakdowns']['patterns']}",
        "",
        "## Entry x stop results",
        "",
        "| Timeframe | Entry | Stop | Zones | Fill % | Target first % | "
        "Stop first % | Median R:R | Median MAE/ATR | Median MFE/ATR |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["summary"]:
        lines.append(
            "| {timeframe} | {entry_policy} | {stop_policy} | {zones} | "
            "{fill_rate_percent:.2f} | {target_before_stop_percent:.2f} | "
            "{stop_before_target_percent:.2f} | {median_structural_rr} | "
            "{median_mae_atr} | {median_mfe_atr} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Look-ahead protection",
            "",
            "- Every accepted zone is re-detected on an OHLCV prefix ending "
            "at its Leg-Out planning candle.",
            "- Wilder ATR(14) is calculated on that prefix only: first ATR "
            "is the mean of 14 True Ranges; later values use Wilder smoothing "
            "`(prior ATR * 13 + TR) / 14`.",
            "- Opposing zones are limited to the same symbol, timeframe, "
            "and prefix snapshot.",
            "- Targets must be directionally ahead, lifecycle-active, and "
            "Authentic at planning time.",
            "- Future candles are read only after the snapshot is frozen "
            "and only for outcome measurement.",
            "- If stop and target are both touched in one candle, the outcome "
            "is recorded as ambiguous rather than guessed.",
            "",
            "## Data limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["limitations"])
    lines.extend(
        [
            "",
            "## Decision status",
            "",
            "No production Entry, Protective Stop, or numerical constants "
            "were selected automatically. Review the row-level JSON and "
            "sensitivity table before approving a policy.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    parser.add_argument("--timeframes", default=",".join(TIMEFRAMES))
    parser.add_argument("--output", default="tmp/trade_planning_replay.json")
    parser.add_argument(
        "--report", default="docs/reports/milestone-8-trade-planning-replay.md"
    )
    parser.add_argument("--maximum-zones-per-segment", type=int, default=8)
    parser.add_argument(
        "--structural-only",
        action="store_true",
        help=(
            "Research optimization: emit one proximal observation per zone. "
            "The placeholder stop is not reported as a canonical protective stop."
        ),
    )
    args = parser.parse_args()
    symbols = tuple(
        item.strip().upper() for item in args.symbols.split(",") if item.strip()
    )
    timeframes = tuple(
        item.strip() for item in args.timeframes.split(",") if item.strip()
    )
    service = MarketDataService()
    engine = TradePlanningReplayEngine()
    snapshots = []
    observations = []
    failures = []
    date_values = []
    started = perf_counter()
    succeeded = 0
    limitations = set()
    logger.setLevel(logging.WARNING)
    for symbol in symbols:
        for timeframe in timeframes:
            try:
                period, interval = source_for(timeframe)
                validated = service.get_stock_data_segments(symbol, period, interval)
                segments = [
                    item
                    for segment in validated.segments
                    if not (item := timeframe_data(segment, timeframe)).empty
                ]
                if not segments:
                    raise ValueError("No valid continuous OHLCV segment")
                succeeded += 1
                for data in segments:
                    replay_options = {}
                    if args.structural_only:
                        replay_options = {
                            "entry_policies": (ReplayEntryPolicy.PROXIMAL,),
                            "stop_policies": (
                                ReplayStopPolicy(
                                    "RESEARCH_ONLY_NOT_CANONICAL_STOP",
                                    zone_width_fraction=0.01,
                                ),
                            ),
                        }
                    result = engine.replay(
                        data,
                        symbol=symbol,
                        timeframe=timeframe,
                        maximum_zones=args.maximum_zones_per_segment,
                        **replay_options,
                    )
                    snapshots.extend(asdict(item) for item in result.snapshots)
                    observations.extend(asdict(item) for item in result.observations)
                    limitations.update(result.limitations)
                    date_values.extend(
                        (
                            comparable_timestamp(data.index[0]),
                            comparable_timestamp(data.index[-1]),
                        )
                    )
            except Exception as error:  # audit keeps provider failures visible
                failures.append(
                    {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "error": type(error).__name__,
                        "message": str(error),
                    }
                )
    # JSON enum values are normalized explicitly for durable audit fixtures.
    for row in observations:
        row["entry_policy"] = row["entry_policy"].value
        row["outcome"] = row["outcome"].value
    payload = {
        "audit": {
            "name": (
                "MILESTONE_9_CANONICAL_ZONE_PERFORMANCE_REPLAY"
                if args.structural_only
                else "MILESTONE_8_HISTORICAL_TRADE_PLANNING_REPLAY"
            ),
            "production_activation": False,
            "structural_only": args.structural_only,
            "duration_seconds": round(perf_counter() - started, 3),
        },
        "dataset": {
            "symbols_requested": len(symbols),
            "symbols": symbols,
            "series_requested": len(symbols) * len(timeframes),
            "series_succeeded": succeeded,
            "series_failed": len(failures),
            "zones_reconstructed": len(snapshots),
            "date_start": str(min(date_values)) if date_values else None,
            "date_end": str(max(date_values)) if date_values else None,
            "provider": type(service._provider).__name__,
            "maximum_zones_per_valid_segment": args.maximum_zones_per_segment,
        },
        "breakdowns": {
            "timeframes": dict(Counter(item["timeframe"] for item in snapshots)),
            "zone_types": dict(Counter(item["zone_type"] for item in snapshots)),
            "patterns": dict(Counter(item["pattern"] for item in snapshots)),
        },
        "summary": summarize(observations),
        "snapshots": snapshots,
        "observations": observations,
        "failures": failures,
        "limitations": sorted(limitations),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {"output": str(output), "report": str(report), **payload["dataset"]},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
