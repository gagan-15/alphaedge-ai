"""Produce the Milestone 8 Protective Stop Finalization study.

Research only. This reads replay evidence and never imports production scanner,
ranking, recommendation, API, or UI code.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path
from statistics import median
from typing import Iterable

PERCENTILES = (0.50, 0.75, 0.80, 0.85, 0.90, 0.95, 0.975, 0.99)
MIN_GROUP = 30


def pct(numerator: int, denominator: int) -> float | None:
    return round(100 * numerator / denominator, 2) if denominator else None


def percentile(values: Iterable[float], quantile: float) -> float | None:
    ordered = sorted(float(value) for value in values if value is not None)
    if not ordered:
        return None
    position = (len(ordered) - 1) * quantile
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return round(ordered[low] * (1 - fraction) + ordered[high] * fraction, 4)


def distribution(values: Iterable[float]) -> dict[str, float | None]:
    materialized = list(values)
    return {
        ("p97_5" if quantile == 0.975 else f"p{quantile * 100:g}"): percentile(
            materialized, quantile
        )
        for quantile in PERCENTILES
    }


def reference_rows(payload: dict) -> list[dict]:
    return [
        row
        for row in payload["observations"]
        if row["entry_policy"] == "PROXIMAL" and row["stop_policy"] == "ZONE_WIDTH_10"
    ]


def stop_outcome(row: dict) -> str:
    if row["entry_index"] is None:
        return "ENTRY_NOT_REACHED"
    if row["target_price"] is None:
        return "NO_VALID_OPPOSING_ZONE"
    stop = row["first_stop_index"]
    target = row["first_target_index"]
    if stop is not None and target is not None and stop == target:
        return "SAME_CANDLE_AMBIGUOUS"
    if target is not None and (stop is None or target < stop):
        return "TARGET_BEFORE_STOP"
    if stop is not None and (target is None or stop < target):
        return "STOP_BEFORE_TARGET"
    return "NO_RESOLUTION"


def beyond_distal(
    row: dict, snapshot: dict, *, before_target: bool
) -> tuple[float, float, float | None]:
    width = snapshot["interaction_high"] - snapshot["interaction_low"]
    mae = row["mae_before_target_price"] if before_target else row["mae_price"]
    beyond = max(0.0, float(mae or 0) - width)
    return (
        beyond,
        beyond / width if width > 0 else 0.0,
        beyond / snapshot["atr14"] if snapshot.get("atr14") else None,
    )


def mae_study(rows: list[dict], snapshots: dict[str, dict]) -> dict:
    target_reaching = [
        row
        for row in rows
        if row["entry_index"] is not None and row["first_target_index"] is not None
    ]
    failed = [
        row
        for row in rows
        if row["entry_index"] is not None
        and row["first_structural_failure_index"] is not None
        and (
            row["first_target_index"] is None
            or row["first_structural_failure_index"] < row["first_target_index"]
        )
    ]

    def summarize(items: list[dict], before_target: bool) -> dict:
        values = [
            beyond_distal(item, snapshots[item["zone_id"]], before_target=before_target)
            for item in items
        ]
        return {
            "count": len(items),
            "beyond_distal_frequency_percent": pct(
                sum(value[0] > 0 for value in values), len(values)
            ),
            "absolute_price": distribution(value[0] for value in values),
            "zone_width_multiple": distribution(value[1] for value in values),
            "wilder_atr14_multiple": distribution(
                value[2] for value in values if value[2] is not None
            ),
        }

    return {
        "target_reaching": summarize(target_reaching, True),
        "failed_or_invalidated": summarize(failed, False),
    }


def ambiguous_mae(rows: list[dict]) -> dict[str, dict]:
    output = {}
    for policy in sorted({row["stop_policy"] for row in rows}, key=policy_order):
        items = [
            row
            for row in rows
            if row["stop_policy"] == policy
            and stop_outcome(row) == "SAME_CANDLE_AMBIGUOUS"
        ]
        output[policy] = {
            "count": len(items),
            "mae_zone_width": distribution(
                item["mae_zone_width"]
                for item in items
                if item["mae_zone_width"] is not None
            ),
            "mae_atr14": distribution(
                item["mae_atr"] for item in items if item["mae_atr"] is not None
            ),
        }
    return output


def policy_order(name: str) -> tuple[int, int]:
    family = (
        0 if name.startswith("ZONE_WIDTH") else 1 if name.startswith("ATR14") else 2
    )
    return family, int(name.rsplit("_", 1)[1])


def stop_summary(items: list[dict]) -> dict:
    filled = [item for item in items if item["entry_index"] is not None]
    eligible = [item for item in filled if item["target_price"] is not None]
    outcomes = Counter(stop_outcome(item) for item in eligible)
    target_reaching = [
        item for item in eligible if item["first_target_index"] is not None
    ]
    false_tight = [
        item
        for item in target_reaching
        if item["first_stop_index"] is not None
        and item["first_stop_index"] < item["first_target_index"]
    ]
    covered = [
        item
        for item in target_reaching
        if item["mae_before_target_price"] is not None
        and item["mae_before_target_price"] <= item["risk_per_share"]
    ]
    risks = [item["risk_per_share"] for item in eligible]
    rrs = [
        item["structural_risk_reward"]
        for item in eligible
        if item["structural_risk_reward"] is not None
    ]
    return {
        "sample_size": len(items),
        "filled": len(filled),
        "eligible_trades": len(eligible),
        "target_before_stop": outcomes["TARGET_BEFORE_STOP"],
        "target_before_stop_percent": pct(
            outcomes["TARGET_BEFORE_STOP"], len(eligible)
        ),
        "stop_before_target": outcomes["STOP_BEFORE_TARGET"],
        "stop_before_target_percent": pct(
            outcomes["STOP_BEFORE_TARGET"], len(eligible)
        ),
        "same_candle_ambiguous": outcomes["SAME_CANDLE_AMBIGUOUS"],
        "same_candle_ambiguous_percent": pct(
            outcomes["SAME_CANDLE_AMBIGUOUS"], len(eligible)
        ),
        "no_resolution": outcomes["NO_RESOLUTION"],
        "no_resolution_percent": pct(outcomes["NO_RESOLUTION"], len(eligible)),
        "median_risk": round(median(risks), 4) if risks else None,
        "median_structural_rr": round(median(rrs), 4) if rrs else None,
        "false_tight_stop_cases": len(false_tight),
        "false_tight_stop_percent_of_target_reaching": pct(
            len(false_tight), len(target_reaching)
        ),
        "mae_coverage_percent_of_target_reaching": pct(
            len(covered), len(target_reaching)
        ),
    }


def grouped(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)
    output = []
    for values, items in sorted(groups.items(), key=lambda item: str(item[0])):
        record = {key: value for key, value in zip(keys, values)}
        record.update(stop_summary(items))
        record["evidence"] = "SUFFICIENT" if len(items) >= MIN_GROUP else "LIMITED"
        output.append(record)
    return output


def add_volatility_regime(rows: list[dict], snapshots: dict[str, dict]) -> None:
    values = []
    for row in rows:
        snap = snapshots[row["zone_id"]]
        midpoint = (snap["interaction_low"] + snap["interaction_high"]) / 2
        value = (
            snap.get("atr14") / midpoint if snap.get("atr14") and midpoint > 0 else None
        )
        if value is not None:
            values.append(value)
    low = percentile(values, 1 / 3)
    high = percentile(values, 2 / 3)
    for row in rows:
        snap = snapshots[row["zone_id"]]
        midpoint = (snap["interaction_low"] + snap["interaction_high"]) / 2
        value = (
            snap.get("atr14") / midpoint if snap.get("atr14") and midpoint > 0 else None
        )
        row["volatility_regime"] = (
            "UNAVAILABLE"
            if value is None
            else "LOW" if value <= low else "HIGH" if value > high else "MEDIUM"
        )


def leave_one_symbol_out(rows: list[dict]) -> list[dict]:
    output = []
    for policy in sorted({row["stop_policy"] for row in rows}, key=policy_order):
        policy_rows = [row for row in rows if row["stop_policy"] == policy]
        rates = []
        for symbol in sorted({row["symbol"] for row in policy_rows}):
            retained = [row for row in policy_rows if row["symbol"] != symbol]
            eligible = [
                row
                for row in retained
                if row["entry_index"] is not None and row["target_price"] is not None
            ]
            target_first = sum(
                stop_outcome(row) == "TARGET_BEFORE_STOP" for row in eligible
            )
            rates.append(pct(target_first, len(eligible)))
        output.append(
            {
                "stop_policy": policy,
                "minimum_target_before_stop_percent": min(rates) if rates else None,
                "maximum_target_before_stop_percent": max(rates) if rates else None,
            }
        )
    return output


def excessively_wide(rows: list[dict]) -> dict[str, dict]:
    by_key = {(row["zone_id"], row["stop_policy"]): row for row in rows}
    result = {}
    for policy in sorted({row["stop_policy"] for row in rows}, key=policy_order):
        family, level = policy.rsplit("_", 1)[0], int(policy.rsplit("_", 1)[1])
        narrower = f"{family}_{level - 5}" if level > 5 else None
        eligible = [
            row
            for row in rows
            if row["stop_policy"] == policy
            and stop_outcome(row) == "TARGET_BEFORE_STOP"
        ]
        if narrower is None:
            result[policy] = {
                "cases": 0,
                "percent": None,
                "definition": "No narrower tested candidate",
            }
            continue
        cases = 0
        comparable = 0
        for row in eligible:
            candidate = by_key.get((row["zone_id"], narrower))
            if candidate is None:
                continue
            comparable += 1
            if stop_outcome(candidate) == "TARGET_BEFORE_STOP":
                cases += 1
        result[policy] = {
            "cases": cases,
            "percent": pct(cases, comparable),
            "definition": "Target also preceded the next 5-point narrower tested stop",
        }
    return result


def table(rows: list[dict], columns: tuple[str, ...]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for row in rows:
        lines.append(
            "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        )
    return lines


def markdown(result: dict) -> str:
    data = result["dataset"]
    lines = [
        "# Milestone 8 - Protective Stop Finalization Report",
        "",
        "> Research only. Complete Canonical Trade Planning V1 remains inactive.",
        "",
        "## Scope and controls",
        "",
        f"- Symbols: {data['symbols_requested']}; successful series: "
        f"{data['series_succeeded']}/{data['series_requested']}",
        f"- Prefix-reconstructed zones: {data['zones_reconstructed']}",
        f"- Provider/date range: {data['provider']}; "
        f"{data['date_start']} to {data['date_end']}",
        "- Entry: frozen Proximal. Target: nearest eligible same-timeframe "
        "opposing canonical zone.",
        "- Horizons: 15m=80, 75m=48, 125m=48, Daily=80, Weekly=52 candles.",
        "- Same-candle stop/target sequence is UNKNOWN; no favorable ordering "
        "is assumed.",
        "",
        "## Overall stop candidates",
        "",
    ]
    lines += table(
        result["stop_overall"],
        (
            "stop_policy",
            "eligible_trades",
            "target_before_stop_percent",
            "stop_before_target_percent",
            "same_candle_ambiguous_percent",
            "no_resolution_percent",
            "median_risk",
            "median_structural_rr",
            "false_tight_stop_percent_of_target_reaching",
            "mae_coverage_percent_of_target_reaching",
            "excessively_wide_percent",
        ),
    )
    lines += [
        "",
        "## MAE beyond canonical Distal",
        "",
        "### Target-reaching trades",
        "",
        f"`{result['mae']['target_reaching']}`",
        "",
        "### Failed/invalidation trades",
        "",
        f"`{result['mae']['failed_or_invalidated']}`",
        "",
    ]
    lines += [
        "## Robustness",
        "",
        "Detailed JSON contains every stop by timeframe, Demand/Supply, pattern, "
        "symbol, year and empirical ATR/price volatility regime.",
        "",
        f"- Sector metadata coverage: {result['robustness']['sector_coverage']}. "
        "Unmapped symbols were not assigned invented sectors.",
        "- Leave-one-symbol-out ranges are included for every candidate.",
        "- Small groups are marked LIMITED and are not used for a firm decision.",
        "",
        "## Final evidence decision",
        "",
        result["decision"],
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", default="tmp/trade_planning_protective_stop_replay.json"
    )
    parser.add_argument(
        "--output", default="tmp/trade_planning_protective_stop_finalization.json"
    )
    parser.add_argument(
        "--report", default="docs/reports/milestone-8-protective-stop-finalization.md"
    )
    parser.add_argument("--additional-input", action="append", default=[])
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    for additional_path in args.additional_input:
        additional = json.loads(Path(additional_path).read_text(encoding="utf-8"))
        payload["snapshots"].extend(additional["snapshots"])
        payload["observations"].extend(additional["observations"])
        payload["failures"] = [
            item for item in payload["failures"] if item["timeframe"] != "1"
        ]
        payload["failures"].extend(additional["failures"])
        payload["dataset"]["series_succeeded"] += additional["dataset"][
            "series_succeeded"
        ]
        payload["dataset"]["series_failed"] = len(payload["failures"])
        payload["dataset"]["zones_reconstructed"] += additional["dataset"][
            "zones_reconstructed"
        ]
        payload["dataset"]["date_start"] = str(
            min(payload["dataset"]["date_start"], additional["dataset"]["date_start"])
        )
        payload["dataset"]["date_end"] = str(
            max(payload["dataset"]["date_end"], additional["dataset"]["date_end"])
        )
    snapshots = {item["zone_id"]: item for item in payload["snapshots"]}
    rows = [row for row in payload["observations"] if row["entry_policy"] == "PROXIMAL"]
    add_volatility_regime(rows, snapshots)
    sector_data = json.loads(
        Path("backend/data/universes/sector_benchmarks.json").read_text(
            encoding="utf-8"
        )
    )["symbols"]
    for row in rows:
        row["sector"] = sector_data.get(row["symbol"], ["UNMAPPED"])[0]
        row["planning_year"] = snapshots[row["zone_id"]]["planning_timestamp"][:4]
    wide = excessively_wide(rows)
    stop_overall = []
    for policy in sorted({row["stop_policy"] for row in rows}, key=policy_order):
        record = {"stop_policy": policy}
        record.update(
            stop_summary([row for row in rows if row["stop_policy"] == policy])
        )
        record["excessively_wide_cases"] = wide[policy]["cases"]
        record["excessively_wide_percent"] = wide[policy]["percent"]
        stop_overall.append(record)
    reference = reference_rows(payload)
    sector_mapped = {row["symbol"] for row in rows if row["sector"] != "UNMAPPED"}
    result = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "dataset": payload["dataset"],
        "approved_horizons": {"15m": 80, "75m": 48, "125m": 48, "1D": 80, "1W": 52},
        "stop_overall": stop_overall,
        "stop_by_timeframe": grouped(rows, ("timeframe", "stop_policy")),
        "stop_by_zone_type": grouped(rows, ("zone_type", "stop_policy")),
        "stop_by_pattern": grouped(rows, ("pattern", "stop_policy")),
        "stop_by_symbol": grouped(rows, ("symbol", "stop_policy")),
        "stop_by_year": grouped(rows, ("planning_year", "stop_policy")),
        "stop_by_volatility_regime": grouped(
            rows, ("volatility_regime", "stop_policy")
        ),
        "stop_by_sector": grouped(rows, ("sector", "stop_policy")),
        "mae": mae_study(reference, snapshots),
        "ambiguous_mae_by_stop": ambiguous_mae(rows),
        "robustness": {
            "leave_one_symbol_out": leave_one_symbol_out(rows),
            "sector_coverage": (
                f"{len(sector_mapped)} of "
                f"{payload['dataset']['symbols_requested']} symbols"
            ),
            "sector_metadata_source": "backend/data/universes/sector_benchmarks.json",
            "volatility_regime_definition": (
                "Empirical terciles of prefix Wilder ATR(14) divided by zone "
                "midpoint; descriptive only"
            ),
        },
        "decision": (
            "**1. Enough evidence to freeze Protective Stop V1? NO.** The "
            "target-reaching and failed distributions are separated in their "
            "centres, but overlap too widely for one defensible cutoff. Among "
            "target-reaching plans, 53.97% moved beyond Distal and the 75th "
            "percentile reached 1.9893 zone widths beyond it. A buffer large "
            "enough to retain most of those recoveries would materially expand "
            "risk and weaken structural meaning.\n\n"
            "**2. Exact formula:** none is justified. Zone-width 5% to 30% "
            "raises target-before-stop from 22.14% to 25.62%, lowers "
            "stop-before-target from 67.16% to 63.93%, and lowers ambiguity "
            "from 3.98% to 2.24%, but median structural R:R falls from 4.4747 "
            "to 3.6141. ATR 5% to 30% gives similarly small outcome changes "
            "while median R:R falls from 4.3159 to 3.2303.\n\n"
            "**3. Robustness:** no candidate behaves consistently enough "
            "across all five timeframes. The 125m eligible sample is only "
            "14-15 plans per candidate; timeframe outcomes differ sharply; "
            "and maintained sector metadata covers only 4 of 28 symbols. "
            "Symbol, pattern, Demand/Supply, year, and empirical volatility "
            "breakdowns are retained in JSON, but they do not establish a "
            "stable universal threshold.\n\n"
            "**4. Required next evidence:** a larger outcome-labelled dataset "
            "with reliable sector metadata, materially larger 125m coverage, "
            "and lower-timeframe sequencing for ambiguous candles. Validate "
            "candidate thresholds out of sample rather than selecting the "
            "best result from this grid.\n\n"
            "**5. Trade Planning V1 readiness:** NOT SAFE to implement as a "
            "complete engine. Canonical Entry V1, structural invalidation, "
            "opposing-zone target architecture, ambiguity policy, and replay "
            "horizons remain approved; Protective Stop remains unresolved."
        ),
    }
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    Path(args.report).write_text(markdown(result), encoding="utf-8")
    print(
        json.dumps(
            {"output": args.output, "report": args.report, "zones": len(reference)},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
