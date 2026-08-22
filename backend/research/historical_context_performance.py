# flake8: noqa: E501
"""Milestone 9B research aggregation for reconstructed ZQ and TC."""

from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Any, Callable

import pandas as pd

from backend.research.historical_zone_performance import wilson_rate


def _first_observations(payloads: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    selected = {}
    snapshots = {
        row["zone_id"]: row for payload in payloads for row in payload["snapshots"]
    }
    for payload in payloads:
        for row in payload["observations"]:
            if row.get("entry_policy") != "PROXIMAL":
                continue
            item = dict(row)
            item.update(
                planning_timestamp=snapshots[row["zone_id"]]["planning_timestamp"]
            )
            selected.setdefault(row["zone_id"], item)
    return selected


def _median(rows, key):
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return round(median(values), 4) if values else None


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    interacted = [row for row in rows if row.get("entry_index") is not None]
    survived = sum(
        row.get("first_structural_failure_index") is None for row in interacted
    )
    reactions = {
        str(level): sum((row.get("mfe_zone_width") or 0) >= level for row in interacted)
        for level in (0.5, 1, 2, 3, 5)
    }
    targets = [row for row in interacted if row.get("target_price") is not None]
    target_hits = sum(row.get("first_target_index") is not None for row in targets)
    n = len(rows)
    return {
        "sample_size": n,
        "reliability": (
            "INSUFFICIENT" if n < 30 else "EXPLORATORY" if n < 100 else "REASONABLE" if n < 300 else "STRONG"
        ),
        "interactions": wilson_rate(len(interacted), n).__dict__,
        "structural_survival": wilson_rate(survived, len(interacted)).__dict__,
        "reactions": {
            level: wilson_rate(value, len(interacted)).__dict__
            for level, value in reactions.items()
        },
        "target_achievement": wilson_rate(target_hits, len(targets)).__dict__,
        "median_mfe_zone_width": _median(interacted, "mfe_zone_width"),
        "median_mae_zone_width": _median(interacted, "mae_zone_width"),
    }


def _group(rows, key: Callable[[dict[str, Any]], str]):
    grouped = defaultdict(list)
    for row in rows:
        grouped[key(row)].append(row)
    return {name: summarize(items) for name, items in sorted(grouped.items())}


def _correlations(rows, score_key):
    if not rows:
        return {}
    frame = pd.DataFrame(
        {
            "score": [row[score_key] for row in rows],
            "survival": [row.get("first_structural_failure_index") is None for row in rows],
            "reaction_2zw": [(row.get("mfe_zone_width") or 0) >= 2 for row in rows],
            "reaction_3zw": [(row.get("mfe_zone_width") or 0) >= 3 for row in rows],
            "mfe": [row.get("mfe_zone_width") for row in rows],
            "target": [row.get("first_target_index") is not None for row in rows],
        }
    )
    return {
        column: round(float(frame["score"].rank().corr(frame[column].rank())), 4)
        if frame[column].notna().sum() > 1 else None
        for column in ("survival", "reaction_2zw", "reaction_3zw", "mfe", "target")
    }


def _ranking(rows):
    groups = defaultdict(list)
    for row in rows:
        date = str(row["planning_timestamp"])[:10]
        groups[(date, row["timeframe"])].append(row)
    buckets = defaultdict(list)
    for items in groups.values():
        if len(items) < 3:
            continue
        ordered = sorted(items, key=lambda row: row["tc_score"], reverse=True)
        size = len(ordered)
        for index, row in enumerate(ordered):
            bucket = "TOP" if index < size / 3 else "MIDDLE" if index < 2 * size / 3 else "LOWER"
            buckets[bucket].append(row)
    return {name: summarize(items) for name, items in sorted(buckets.items())}


def analyze(
    replay_payloads: list[dict[str, Any]], context_payloads: list[dict[str, Any]]
) -> dict[str, Any]:
    outcomes = _first_observations(replay_payloads)
    contexts = {
        row["zone_id"]: row for payload in context_payloads for row in payload["records"]
    }
    merged = []
    zq_coverage = defaultdict(int)
    tc_coverage = defaultdict(int)
    unavailable_reasons = defaultdict(int)
    for zone_id, outcome in outcomes.items():
        context = contexts.get(zone_id)
        if context is None:
            zq_coverage["UNAVAILABLE"] += 1
            tc_coverage["UNAVAILABLE"] += 1
            unavailable_reasons["CONTEXT_RECORD_MISSING"] += 1
            continue
        zq_status = context["zone_quality"]["status"]
        tc_status = context["trade_confidence"]["status"]
        zq_coverage[zq_status] += 1
        tc_coverage[tc_status] += 1
        if zq_status != "AVAILABLE" or tc_status != "AVAILABLE":
            unavailable_reasons[
                context["zone_quality"].get("reason", "UNKNOWN")
            ] += 1
            continue
        row = dict(outcome)
        row.update(
            zq_score=context["zone_quality"]["score"],
            zq_label=context["zone_quality"]["label"],
            tc_score=context["trade_confidence"]["score"],
            tc_label=context["trade_confidence"]["label"],
            tc_sufficiency=context["trade_confidence"]["data_sufficiency"],
            htf_compatibility=context["trade_confidence"]["htf_compatibility"],
            htf_relationship=context["trade_confidence"]["htf_relationship"],
            trend_alignment=context["trade_confidence"]["trend_alignment"],
            conflicted=context["trade_confidence"]["conflicted"],
        )
        row["context_class"] = (
            "CONFLICTED" if row["conflicted"] else
            "ALIGNED" if row["htf_compatibility"] == "ALIGNED" and row["trend_alignment"] == "ALIGNED" else
            "NEUTRAL_OR_PARTIAL"
        )
        merged.append(row)
    matrix = _group(merged, lambda row: f"{row['zq_label']} x {row['tc_label']}")
    within_zq_context = _group(
        merged, lambda row: f"{row['zq_label']} x {row['context_class']}"
    )
    within_zq_htf = _group(
        merged,
        lambda row: (
            f"{row['zq_label']} x HTF {row['htf_compatibility']} "
            f"{row['htf_relationship']}"
        ),
    )
    within_zq_trend = _group(
        merged,
        lambda row: f"{row['zq_label']} x Trend {row['trend_alignment']}",
    )
    return {
        "dataset": {
            "historical_zones": len(outcomes),
            "available_records": len(merged),
        },
        "coverage": {
            "zone_quality": dict(zq_coverage),
            "trade_confidence": dict(tc_coverage),
            "unavailable_reasons": dict(unavailable_reasons),
        },
        "zone_quality": {
            "bands": _group(merged, lambda row: row["zq_label"]),
            "rank_correlations": _correlations(merged, "zq_score"),
        },
        "trade_confidence": {
            "labels": _group(merged, lambda row: row["tc_label"]),
            "numeric_bands": _group(
                merged,
                lambda row: "85-100" if row["tc_score"] >= 85 else "70-84.99" if row["tc_score"] >= 70 else "50-69.99" if row["tc_score"] >= 50 else "0-49.99",
            ),
            "rank_correlations": _correlations(merged, "tc_score"),
        },
        "matrix": matrix,
        "incremental_context_within_zq": within_zq_context,
        "incremental_htf_within_zq": within_zq_htf,
        "incremental_trend_within_zq": within_zq_trend,
        "by_timeframe_zq": _group(merged, lambda row: f"{row['timeframe']} x {row['zq_label']}"),
        "by_timeframe_tc": _group(merged, lambda row: f"{row['timeframe']} x {row['tc_label']}"),
        "by_zone_type": _group(merged, lambda row: f"{row['zone_type']} x {row['tc_label']}"),
        "by_pattern": _group(merged, lambda row: f"{row['pattern']} x {row['tc_label']}"),
        "by_year": _group(merged, lambda row: f"{str(row['planning_timestamp'])[:4]} x {row['tc_label']}"),
        "dashboard_ranking": _ranking(merged),
    }
