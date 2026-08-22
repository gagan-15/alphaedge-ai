"""Create the Milestone 8 final calibration report from replay evidence.

Research-only analysis. It reads the durable replay JSON and never imports or
changes production scanner, ranking, recommendation, or UI behavior.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path
from statistics import median
from typing import Iterable

MIN_SUBGROUP_SAMPLE = 30
ENTRY_REFERENCE_STOP = "ZONE_WIDTH_10"
HORIZONS = {
    "15m": (20, 40, 80, 160),
    "75m": (12, 24, 48, 96),
    "125m": (12, 24, 48, 96),
    "1D": (20, 40, 80, 160),
    "1W": (8, 13, 26, 52),
}


def percent(count: int, denominator: int) -> float | None:
    return round(100 * count / denominator, 2) if denominator else None


def percentile(values: Iterable[float], quantile: float) -> float | None:
    ordered = sorted(float(value) for value in values if value is not None)
    if not ordered:
        return None
    position = (len(ordered) - 1) * quantile
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return round(ordered[low] * (1 - fraction) + ordered[high] * fraction, 4)


def quantiles(values: Iterable[float]) -> dict[str, float | None]:
    materialized = list(values)
    return {
        "p50": percentile(materialized, 0.50),
        "p75": percentile(materialized, 0.75),
        "p80": percentile(materialized, 0.80),
        "p90": percentile(materialized, 0.90),
        "p95": percentile(materialized, 0.95),
    }


def unique_reference_rows(payload: dict, entry: str = "PROXIMAL") -> list[dict]:
    return [
        row
        for row in payload["observations"]
        if row["entry_policy"] == entry and row["stop_policy"] == ENTRY_REFERENCE_STOP
    ]


def structural_outcome(row: dict) -> str:
    if row["entry_index"] is None:
        return "ENTRY_NOT_REACHED"
    if row["target_price"] is None:
        return "NO_VALID_TARGET"
    target = row["first_target_index"]
    failure = row["first_structural_failure_index"]
    if target is not None and failure is not None and target == failure:
        return "SAME_CANDLE_AMBIGUOUS"
    if target is not None and (failure is None or target < failure):
        return "TARGET_BEFORE_INVALIDATION"
    if failure is not None and (target is None or failure < target):
        return "INVALIDATION_BEFORE_TARGET"
    return "UNRESOLVED_WITHIN_DATA"


def subgroup(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)
    output = []
    for group_key, items in sorted(groups.items(), key=lambda item: str(item[0])):
        entered = [item for item in items if item["entry_index"] is not None]
        outcomes = Counter(structural_outcome(item) for item in items)
        candles = [item["candles_to_entry"] for item in entered]
        maes = [item["mae_zone_width"] for item in entered]
        mfes = [item["mfe_zone_width"] for item in entered]
        record = {key: value for key, value in zip(keys, group_key)}
        record.update(
            {
                "sample_size": len(items),
                "evidence": (
                    "SUFFICIENT" if len(items) >= MIN_SUBGROUP_SAMPLE else "LIMITED"
                ),
                "fill_rate_percent": percent(len(entered), len(items)),
                "median_candles_to_fill": (
                    round(median(candles), 2) if candles else None
                ),
                "target_before_invalidation_percent": percent(
                    outcomes["TARGET_BEFORE_INVALIDATION"], len(items)
                ),
                "invalidation_before_target_percent": percent(
                    outcomes["INVALIDATION_BEFORE_TARGET"], len(items)
                ),
                "no_valid_target_percent": percent(
                    outcomes["NO_VALID_TARGET"], len(items)
                ),
                "unresolved_percent": percent(
                    outcomes["UNRESOLVED_WITHIN_DATA"], len(items)
                ),
                "same_candle_ambiguous_percent": percent(
                    outcomes["SAME_CANDLE_AMBIGUOUS"], len(items)
                ),
                "median_mae_zone_width": round(median(maes), 4) if maes else None,
                "median_mfe_zone_width": round(median(mfes), 4) if mfes else None,
            }
        )
        output.append(record)
    return output


def leave_one_symbol_out(rows: list[dict]) -> list[dict]:
    symbols = sorted({row["symbol"] for row in rows})
    output = []
    for symbol in symbols:
        retained = [row for row in rows if row["symbol"] != symbol]
        fills = sum(row["entry_index"] is not None for row in retained)
        output.append(
            {
                "removed_symbol": symbol,
                "remaining_zones": len(retained),
                "fill_rate_percent": percent(fills, len(retained)),
            }
        )
    return output


def period_robustness(rows: list[dict], snapshots: dict[str, dict]) -> list[dict]:
    years: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        raw = snapshots[row["zone_id"]]["planning_timestamp"]
        year = str(raw)[:4]
        years[year].append(row)
    return [
        {
            "year": year,
            "sample_size": len(items),
            "evidence": (
                "SUFFICIENT" if len(items) >= MIN_SUBGROUP_SAMPLE else "LIMITED"
            ),
            "fill_rate_percent": percent(
                sum(item["entry_index"] is not None for item in items), len(items)
            ),
        }
        for year, items in sorted(years.items())
    ]


def same_candle(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if row["entry_policy"] == "PROXIMAL":
            groups[(row["timeframe"], row["stop_policy"])].append(row)
    output = []
    for (timeframe, policy), items in sorted(groups.items()):
        eligible = [
            row
            for row in items
            if row["entry_index"] is not None and row["target_price"] is not None
        ]
        actual = Counter(row["outcome"] for row in eligible)
        ambiguous = actual["AMBIGUOUS_SAME_CANDLE"]
        output.append(
            {
                "timeframe": timeframe,
                "stop_policy": policy,
                "eligible": len(eligible),
                "ambiguous": ambiguous,
                "ambiguous_percent": percent(ambiguous, len(eligible)),
                "conservative_stop_first": actual["STOP_BEFORE_TARGET"] + ambiguous,
                "optimistic_target_first": actual["TARGET_BEFORE_STOP"] + ambiguous,
                "explicit_unknown": ambiguous,
            }
        )
    return output


def stop_study(payload: dict) -> list[dict]:
    rows = [row for row in payload["observations"] if row["entry_policy"] == "PROXIMAL"]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["timeframe"], row["stop_policy"])].append(row)
    output = []
    for (timeframe, policy), items in sorted(groups.items()):
        filled = [item for item in items if item["entry_index"] is not None]
        eligible = [item for item in filled if item["target_price"] is not None]
        outcomes = Counter(item["outcome"] for item in eligible)
        risks = [item["risk_per_share"] for item in filled]
        rrs = [
            item["structural_risk_reward"]
            for item in eligible
            if item["structural_risk_reward"] is not None
        ]
        eventual = [item for item in eligible if item["first_target_index"] is not None]
        marginal = 0
        for item in eventual:
            if item["first_stop_index"] is None:
                continue
            if item["first_stop_index"] <= item["first_target_index"]:
                overshoot = (item["mae_before_target_price"] or 0) - item[
                    "risk_per_share"
                ]
                width = item["risk_per_share"]
                if policy.startswith("ZONE_WIDTH_"):
                    fraction = int(policy.rsplit("_", 1)[1]) / 100
                    width = item["risk_per_share"] / (1 + fraction)
                if width > 0 and overshoot <= 0.05 * width:
                    marginal += 1
        output.append(
            {
                "timeframe": timeframe,
                "stop_policy": policy,
                "sample_size": len(items),
                "filled": len(filled),
                "valid_target_filled": len(eligible),
                "target_before_stop": outcomes["TARGET_BEFORE_STOP"],
                "stop_before_target": outcomes["STOP_BEFORE_TARGET"],
                "ambiguous": outcomes["AMBIGUOUS_SAME_CANDLE"],
                "median_risk_per_share": round(median(risks), 4) if risks else None,
                "median_structural_rr": round(median(rrs), 4) if rrs else None,
                "marginal_stop_then_target": marginal,
                "marginal_stop_then_target_percent": percent(marginal, len(eventual)),
            }
        )
    return output


def mae_study(rows: list[dict], snapshots: dict[str, dict]) -> dict:
    valid_successes = [
        row for row in rows if structural_outcome(row) == "TARGET_BEFORE_INVALIDATION"
    ]
    recovered_after_failure = [
        row
        for row in rows
        if row["first_target_index"] is not None
        and row["first_structural_failure_index"] is not None
        and row["first_structural_failure_index"] < row["first_target_index"]
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

    def beyond_distal(item: dict, before_target: bool) -> tuple[float, float | None]:
        snap = snapshots[item["zone_id"]]
        width = snap["interaction_high"] - snap["interaction_low"]
        mae = (
            item["mae_before_target_price"] if before_target else item["mae_price"]
        ) or 0
        beyond = max(0.0, mae - width)
        atr = snap["atr14"]
        return beyond / width if width > 0 else 0.0, beyond / atr if atr else None

    success_values = [beyond_distal(item, True) for item in valid_successes]
    recovered_values = [beyond_distal(item, True) for item in recovered_after_failure]
    failed_values = [beyond_distal(item, False) for item in failed]
    return {
        "valid_target_before_invalidation_count": len(valid_successes),
        "target_after_structural_failure_count": len(recovered_after_failure),
        "failed_before_target_count": len(failed),
        "successful_beyond_distal_zone_width": quantiles(
            value[0] for value in success_values
        ),
        "successful_beyond_distal_atr": quantiles(
            value[1] for value in success_values if value[1] is not None
        ),
        "recovered_after_failure_beyond_distal_zone_width": quantiles(
            value[0] for value in recovered_values
        ),
        "recovered_after_failure_beyond_distal_atr": quantiles(
            value[1] for value in recovered_values if value[1] is not None
        ),
        "failed_beyond_distal_zone_width": quantiles(
            value[0] for value in failed_values
        ),
        "failed_beyond_distal_atr": quantiles(
            value[1] for value in failed_values if value[1] is not None
        ),
    }


def horizon_study(rows: list[dict]) -> list[dict]:
    output = []
    for timeframe, candidates in HORIZONS.items():
        items = [
            row
            for row in rows
            if row["timeframe"] == timeframe and row["entry_index"] is not None
        ]
        for horizon in candidates:
            resolved = 0
            target = 0
            invalidation = 0
            ambiguous = 0
            for item in items:
                target_offset = (
                    None
                    if item["first_target_index"] is None
                    else item["first_target_index"] - item["entry_index"] + 1
                )
                failure_offset = (
                    None
                    if item["first_structural_failure_index"] is None
                    else item["first_structural_failure_index"]
                    - item["entry_index"]
                    + 1
                )
                target_in = target_offset is not None and target_offset <= horizon
                failure_in = failure_offset is not None and failure_offset <= horizon
                if target_in and failure_in and target_offset == failure_offset:
                    ambiguous += 1
                    resolved += 1
                elif target_in and (not failure_in or target_offset < failure_offset):
                    target += 1
                    resolved += 1
                elif failure_in:
                    invalidation += 1
                    resolved += 1
            output.append(
                {
                    "timeframe": timeframe,
                    "horizon_candles": horizon,
                    "filled_sample": len(items),
                    "resolved": resolved,
                    "resolved_percent": percent(resolved, len(items)),
                    "target_first": target,
                    "invalidation_first": invalidation,
                    "ambiguous": ambiguous,
                }
            )
    return output


def target_reasons(payload: dict) -> dict:
    return dict(
        Counter(item["target_availability_reason"] for item in payload["snapshots"])
    )


def entry_comparison(payload: dict) -> list[dict]:
    output = []
    for entry in ("PROXIMAL", "MIDPOINT", "DISTAL"):
        rows = unique_reference_rows(payload, entry)
        entered = [row for row in rows if row["entry_index"] is not None]
        output.append(
            {
                "entry": entry,
                "sample_size": len(rows),
                "filled": len(entered),
                "fill_rate_percent": percent(len(entered), len(rows)),
                "median_candles_to_fill": (
                    round(median(row["candles_to_entry"] for row in entered), 2)
                    if entered
                    else None
                ),
            }
        )
    return output


def wider_than_needed_percent(
    payload: dict,
    policy: str,
    eligible: list[dict],
) -> float | None:
    """Report ex-post stop width only; never select a production policy."""

    observations = {
        (row["zone_id"], row["stop_policy"]): row
        for row in payload["observations"]
        if row["entry_policy"] == "PROXIMAL"
    }
    prefix, raw_level = policy.rsplit("_", 1)
    level = int(raw_level)
    narrower = f"{prefix}_{level - 5}" if level > 5 else None
    count = 0
    denominator = 0
    for row in eligible:
        target = row["first_target_index"]
        if target is None:
            continue
        denominator += 1
        if narrower is None:
            failure = row["first_structural_failure_index"]
            survived = failure is None or target < failure
        else:
            candidate = observations.get((row["zone_id"], narrower))
            if candidate is None:
                denominator -= 1
                continue
            stop = candidate["first_stop_index"]
            survived = stop is None or target < stop
        count += survived
    return percent(count, denominator)


def render_table(rows: list[dict], columns: tuple[str, ...]) -> list[str]:
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
    dataset = result["dataset"]
    overall = result["proximal_overall"]
    lines = [
        "# Milestone 8 - Final Trade Planning Calibration Study",
        "",
        "> Research only. Canonical Trade Planning V1 remains inactive.",
        "",
        "## Evidence and scope",
        "",
        f"- Replay generated: {result['generated_at']}",
        f"- Symbols: {dataset['symbols_requested']} ({', '.join(dataset['symbols'])})",
        f"- Series succeeded/failed: {dataset['series_succeeded']} / {dataset['series_failed']}",  # noqa: E501
        f"- Prefix-reconstructed zones: {dataset['zones_reconstructed']}",
        f"- Provider: {dataset['provider']}",
        f"- Date range: {dataset['date_start']} to {dataset['date_end']}",
        "- Symbols were the original accepted 12 plus a deterministic, evenly spaced NSE 500 expansion; no outcome-based symbol selection was used.",  # noqa: E501
        "- Subgroups below 30 zones are marked LIMITED and are not used for firm conclusions.",  # noqa: E501
        "",
        "## Proximal entry validation",
        "",
        f"Overall fill: {overall['filled']} / {overall['zones']} ({overall['fill_rate_percent']}%). Median candles to fill: {overall['median_candles_to_fill']}.",  # noqa: E501
        "",
        "| Entry | Sample | Filled | Fill % | Median candles |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in result["entry_comparison"]:
        lines.append(
            f"| {item['entry']} | {item['sample_size']} | {item['filled']} | "
            f"{item['fill_rate_percent']} | {item['median_candles_to_fill']} |"
        )
    lines += [
        "",
        "### By timeframe",
        "",
    ]
    lines += render_table(
        result["proximal_by_timeframe"],
        (
            "timeframe",
            "sample_size",
            "evidence",
            "fill_rate_percent",
            "median_candles_to_fill",
            "target_before_invalidation_percent",
            "invalidation_before_target_percent",
            "no_valid_target_percent",
            "median_mae_zone_width",
            "median_mfe_zone_width",
        ),
    )
    lines += ["", "### By zone type", ""]
    lines += render_table(
        result["proximal_by_zone_type"],
        (
            "zone_type",
            "sample_size",
            "evidence",
            "fill_rate_percent",
            "median_candles_to_fill",
            "target_before_invalidation_percent",
            "invalidation_before_target_percent",
            "no_valid_target_percent",
        ),
    )
    lines += ["", "### By pattern", ""]
    lines += render_table(
        result["proximal_by_pattern"],
        (
            "pattern",
            "sample_size",
            "evidence",
            "fill_rate_percent",
            "median_candles_to_fill",
            "target_before_invalidation_percent",
            "invalidation_before_target_percent",
            "no_valid_target_percent",
        ),
    )
    lines += [
        "",
        "## Robustness",
        "",
        f"Leave-one-symbol-out fill range: {result['robustness']['loo_min_fill']}% to {result['robustness']['loo_max_fill']}%.",  # noqa: E501
        "",
        "### Period stability",
        "",
    ]
    lines += render_table(
        result["robustness"]["by_year"],
        ("year", "sample_size", "evidence", "fill_rate_percent"),
    )
    lines += [
        "",
        "## Same-candle ambiguity",
        "",
        "OHLC cannot establish sequence when stop and target are both inside one candle. The canonical research recommendation is UNKNOWN / SAME_CANDLE_AMBIGUOUS; conservative and optimistic counts are sensitivity bounds only.",  # noqa: E501
        "",
    ]
    lines += render_table(
        result["same_candle_summary"],
        (
            "stop_policy",
            "eligible",
            "ambiguous",
            "ambiguous_percent",
            "conservative_stop_first",
            "optimistic_target_first",
            "explicit_unknown",
        ),
    )
    lines += [
        "",
        "## Protective-stop calibration",
        "",
        "The detailed JSON contains every timeframe x stop candidate. No candidate is selected by win rate. 'Marginal' means the stop was exceeded by no more than 5% of zone width before a later target; it is descriptive, not a proposed rule.",  # noqa: E501
        "",
    ]
    lines += render_table(
        result["stop_overall"],
        (
            "stop_policy",
            "filled",
            "valid_target_filled",
            "target_before_stop",
            "stop_before_target",
            "ambiguous",
            "median_risk_per_share",
            "median_structural_rr",
            "marginal_stop_then_target_percent",
            "wider_than_needed_ex_post_percent",
        ),
    )
    lines += ["", "## MAE beyond structural Distal", ""]
    mae = result["mae"]
    lines += [
        f"- Valid target-before-invalidation observations: {mae['valid_target_before_invalidation_count']}",  # noqa: E501
        f"- Target reached only after structural failure: {mae['target_after_structural_failure_count']}",  # noqa: E501
        f"- Structural-failure-before-target observations: {mae['failed_before_target_count']}",  # noqa: E501
        f"- Successful zone-width percentiles: {mae['successful_beyond_distal_zone_width']}",  # noqa: E501
        f"- Successful ATR percentiles: {mae['successful_beyond_distal_atr']}",
        f"- Later-recovery zone-width percentiles: {mae['recovered_after_failure_beyond_distal_zone_width']}",  # noqa: E501
        f"- Later-recovery ATR percentiles: {mae['recovered_after_failure_beyond_distal_atr']}",  # noqa: E501
        f"- Failed zone-width percentiles: {mae['failed_beyond_distal_zone_width']}",
        f"- Failed ATR percentiles: {mae['failed_beyond_distal_atr']}",
        "",
        "## Target availability",
        "",
    ]
    target_total = sum(result["target_reasons"].values())
    for reason, count in sorted(result["target_reasons"].items()):
        lines.append(f"- {reason}: {count} ({percent(count, target_total)}%)")
    lines += ["", "## Replay horizon sensitivity", ""]
    lines += render_table(
        result["horizons"],
        (
            "timeframe",
            "horizon_candles",
            "filled_sample",
            "resolved",
            "resolved_percent",
            "target_first",
            "invalidation_first",
            "ambiguous",
        ),
    )
    lines += [
        "",
        "## Tick size",
        "",
        "Official NSE master-data specifications include a per-security Tick Size field, so trustworthy metadata can be incorporated through a maintained NSE security-master ingestion path. The current YahooProvider contract does not expose it, and this study did not download or hard-code an unverified substitute. No universal Rs 0.05 assumption was made. Source: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE-Masters%20Data-v1.6.pdf",  # noqa: E501
        "",
        "## Look-ahead validation",
        "",
        "- Entry and boundaries come from the prefix-reconstructed selected zone.",
        "- Wilder ATR(14) uses the planning prefix only.",
        "- Opposing targets must exist in the same symbol/timeframe prefix snapshot.",
        "- Lifecycle and authenticity are evaluated from that prefix snapshot.",
        "- Future zones are used only to classify why a target was unavailable, never to create a plan target.",  # noqa: E501
        "- Future candles affect outcomes only after planning coordinates are frozen.",
        "",
        "## Final decision",
        "",
        result["decision"],
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="tmp/trade_planning_final_replay.json")
    parser.add_argument("--output", default="tmp/trade_planning_final_calibration.json")
    parser.add_argument(
        "--report", default="docs/reports/milestone-8-final-calibration.md"
    )
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = unique_reference_rows(payload)
    snapshots = {item["zone_id"]: item for item in payload["snapshots"]}
    entered = [row for row in rows if row["entry_index"] is not None]
    loo = leave_one_symbol_out(rows)
    stops = stop_study(payload)
    stop_overall = []
    for policy in sorted({item["stop_policy"] for item in stops}):
        items = [
            row
            for row in payload["observations"]
            if row["entry_policy"] == "PROXIMAL" and row["stop_policy"] == policy
        ]
        filled_items = [item for item in items if item["entry_index"] is not None]
        eligible = [item for item in filled_items if item["target_price"] is not None]
        outcomes = Counter(item["outcome"] for item in eligible)
        risks = [item["risk_per_share"] for item in filled_items]
        rrs = [
            item["structural_risk_reward"]
            for item in eligible
            if item["structural_risk_reward"] is not None
        ]
        related = [item for item in stops if item["stop_policy"] == policy]
        marginal_numerator = sum(item["marginal_stop_then_target"] for item in related)
        eventual = sum(1 for item in eligible if item["first_target_index"] is not None)
        stop_overall.append(
            {
                "stop_policy": policy,
                "filled": len(filled_items),
                "valid_target_filled": len(eligible),
                "target_before_stop": outcomes["TARGET_BEFORE_STOP"],
                "stop_before_target": outcomes["STOP_BEFORE_TARGET"],
                "ambiguous": outcomes["AMBIGUOUS_SAME_CANDLE"],
                "median_risk_per_share": round(median(risks), 4) if risks else None,
                "median_structural_rr": round(median(rrs), 4) if rrs else None,
                "marginal_stop_then_target_percent": percent(
                    marginal_numerator, eventual
                ),
                "wider_than_needed_ex_post_percent": wider_than_needed_percent(
                    payload, policy, eligible
                ),
            }
        )
    ambiguities = same_candle(payload["observations"])
    ambiguity_overall = []
    for policy in sorted({item["stop_policy"] for item in ambiguities}):
        items = [item for item in ambiguities if item["stop_policy"] == policy]
        ambiguity_overall.append(
            {
                "stop_policy": policy,
                "eligible": sum(item["eligible"] for item in items),
                "ambiguous": sum(item["ambiguous"] for item in items),
                "ambiguous_percent": percent(
                    sum(item["ambiguous"] for item in items),
                    sum(item["eligible"] for item in items),
                ),
                "conservative_stop_first": sum(
                    item["conservative_stop_first"] for item in items
                ),
                "optimistic_target_first": sum(
                    item["optimistic_target_first"] for item in items
                ),
                "explicit_unknown": sum(item["explicit_unknown"] for item in items),
            }
        )
    result = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "dataset": payload["dataset"],
        "proximal_overall": {
            "zones": len(rows),
            "filled": len(entered),
            "fill_rate_percent": percent(len(entered), len(rows)),
            "median_candles_to_fill": (
                round(median(item["candles_to_entry"] for item in entered), 2)
                if entered
                else None
            ),
        },
        "entry_comparison": entry_comparison(payload),
        "proximal_by_timeframe": subgroup(rows, ("timeframe",)),
        "proximal_by_zone_type": subgroup(rows, ("zone_type",)),
        "proximal_by_pattern": subgroup(rows, ("pattern",)),
        "proximal_by_symbol": subgroup(rows, ("symbol",)),
        "robustness": {
            "leave_one_symbol_out": loo,
            "loo_min_fill": min(item["fill_rate_percent"] for item in loo),
            "loo_max_fill": max(item["fill_rate_percent"] for item in loo),
            "by_year": period_robustness(rows, snapshots),
        },
        "same_candle_by_timeframe": ambiguities,
        "same_candle_summary": ambiguity_overall,
        "stop_by_timeframe": stops,
        "stop_overall": stop_overall,
        "mae": mae_study(rows, snapshots),
        "target_reasons": target_reasons(payload),
        "horizons": horizon_study(rows),
        "decision": (
            "**Entry:** Freeze Proximal as Canonical Entry V1 only if the owner "
            "accepts it as the interaction coordinate, not as a promised fill. "
            "It leads Midpoint and Distal overall and on every timeframe; "
            "leave-one-symbol-out fill varies by less than one percentage point.\n\n"
            "**Protective Stop:** Do not freeze any tested buffer. The 5%-20% "
            "zone-width, ATR, and hybrid candidates change relatively few "
            "target-first outcomes, while every valid target-before-invalidation "
            "case has zero excursion beyond Distal by definition. No exact stop "
            "formula is supported.\n\n"
            "**Target:** Retain the same-timeframe nearest active Authentic "
            "opposing canonical zone. Availability is limited and missing "
            "targets must not be manufactured.\n\n"
            "**Horizon candidates for further validation:** 15m=80 candles, "
            "75m=48, 125m=48, 1D=80, 1W=52. These are saturation-based research "
            "windows, not frozen production rules.\n\n"
            "**Same-candle ambiguity:** Keep UNKNOWN / "
            "SAME_CANDLE_AMBIGUOUS as canonical research treatment. Use stop-first "
            "and target-first only as conservative/optimistic sensitivity bounds.\n\n"
            "**Implementation readiness:** Canonical Trade Planning V1 is not "
            "safe to implement as a complete engine because Protective Stop and "
            "replay horizon remain unresolved. Proximal Entry and opposing-zone "
            "Target architecture have sufficient evidence for separate owner "
            "approval."
        ),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(markdown(result), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output),
                "report": str(report),
                **result["proximal_overall"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
