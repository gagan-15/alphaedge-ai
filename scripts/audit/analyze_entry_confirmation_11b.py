"""Summarize the frozen Milestone 11B research replay.

Research only. This module is not imported by production code.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from math import sqrt
from pathlib import Path
from statistics import median

TIERS = {
    "tier_1_close_recovery": "close_recovery",
    "tier_2_reaction_detected": "reaction_detected",
    "tier_3_structural_confirmation": "structural_confirmation",
}


def wilson(successes: int, count: int) -> list[float] | None:
    if not count:
        return None
    z = 1.96
    probability = successes / count
    denominator = 1 + z * z / count
    center = (probability + z * z / (2 * count)) / denominator
    margin = (
        z
        * sqrt((probability * (1 - probability) + z * z / (4 * count)) / count)
        / denominator
    )
    return [round(100 * (center - margin), 2), round(100 * (center + margin), 2)]


def summarize(rows: list[dict]) -> dict:
    baseline_two = sum(row["mfe_zone_width_from_interaction"] >= 2 for row in rows)
    result = {
        "observations": len(rows),
        "baseline_1zw": sum(
            row["mfe_zone_width_from_interaction"] >= 1 for row in rows
        ),
        "baseline_2zw": baseline_two,
        "baseline_3zw": sum(
            row["mfe_zone_width_from_interaction"] >= 3 for row in rows
        ),
        "baseline_2zw_percent": (
            round(100 * baseline_two / len(rows), 2) if rows else None
        ),
        "baseline_2zw_wilson_95": wilson(baseline_two, len(rows)),
        "tiers": {},
    }
    for tier, prefix in TIERS.items():
        selected = [row for row in rows if row.get(f"{prefix}_index") is not None]
        post = [row[f"{prefix}_post_mfe_zw"] for row in selected]
        two = sum(value >= 2 for value in post)
        strong_missed = sum(
            row["mfe_zone_width_from_interaction"] >= 2
            and row.get(f"{prefix}_index") is None
            for row in rows
        )
        result["tiers"][tier] = {
            "observations": len(selected),
            "coverage_percent": (
                round(100 * len(selected) / len(rows), 2) if rows else None
            ),
            "post_1zw": sum(value >= 1 for value in post),
            "post_2zw": two,
            "post_3zw": sum(value >= 3 for value in post),
            "post_2zw_percent": round(100 * two / len(post), 2) if post else None,
            "post_2zw_wilson_95": wilson(two, len(post)),
            "median_post_mfe_zw": round(median(post), 4) if post else None,
            "median_pre_move_zw": (
                round(median(row[f"{prefix}_pre_move_zw"] for row in selected), 4)
                if selected
                else None
            ),
            "subsequent_failure": sum(
                row["structural_failure_index"] is not None
                and row["structural_failure_index"] >= row[f"{prefix}_index"]
                for row in selected
            ),
            "weak_post_reaction": sum(value < 1 for value in post),
            "strong_reactions_missed": strong_missed,
            "strong_reactions_missed_percent": (
                round(100 * strong_missed / baseline_two, 2) if baseline_two else None
            ),
            "same_candle_ambiguous": sum(
                row[f"{prefix}_index"] == row["interaction_index"] for row in selected
            ),
        }
    return result


def grouped(records: list[dict], key) -> dict:
    groups = defaultdict(list)
    for row in records:
        groups[key(row)].append(row)
    return {str(name): summarize(rows) for name, rows in sorted(groups.items())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    records = source["records"]
    per_symbol = grouped(records, lambda row: row["symbol"])
    symbol_tier_rates = {}
    for tier in TIERS:
        rates = [
            values["tiers"][tier]["post_2zw_percent"]
            for values in per_symbol.values()
            if values["tiers"][tier]["observations"] >= 10
        ]
        symbol_tier_rates[tier] = {
            "eligible_symbols": len(rates),
            "median_symbol_post_2zw_percent": (
                round(median(rates), 2) if rates else None
            ),
            "min": min(rates) if rates else None,
            "max": max(rates) if rates else None,
        }
    payload = {
        "audit": "MILESTONE_11B_ANALYSIS",
        "production_activation": False,
        "overall": summarize(records),
        "by_side": grouped(records, lambda row: row["zone_type"]),
        "by_pattern": grouped(records, lambda row: row["pattern"]),
        "by_timeframe": grouped(records, lambda row: row["timeframe"]),
        "by_period": grouped(
            records,
            lambda row: (
                "2021-2022"
                if row["interaction_timestamp"][:4] <= "2022"
                else (
                    "2023-2024"
                    if row["interaction_timestamp"][:4] <= "2024"
                    else "2025-2026"
                )
            ),
        ),
        "symbol_robustness": symbol_tier_rates,
        "representative_cases": {
            "strong_useful": sorted(
                [
                    row
                    for row in records
                    if row.get("structural_confirmation_index") is not None
                    and row["structural_confirmation_post_mfe_zw"] >= 3
                ],
                key=lambda row: row["structural_confirmation_post_mfe_zw"],
                reverse=True,
            )[:8],
            "false_confirmation": [
                row
                for row in records
                if row.get("structural_confirmation_index") is not None
                and row["structural_confirmation_post_mfe_zw"] < 1
            ][:8],
            "missed_explosive": sorted(
                [
                    row
                    for row in records
                    if row.get("reaction_detected_index") is None
                    and row["mfe_zone_width_from_interaction"] >= 3
                ],
                key=lambda row: row["mfe_zone_width_from_interaction"],
                reverse=True,
            )[:8],
            "no_confirmation": [
                row
                for row in records
                if row.get("close_recovery_index") is None
                and row.get("reaction_detected_index") is None
                and row.get("structural_confirmation_index") is None
            ][:8],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
