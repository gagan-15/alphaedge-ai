# flake8: noqa: E501
"""Milestone 9C research-only aggregation.

This module analyzes immutable point-in-time replay records.  It does not
import a production scanner or change any production methodology.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from math import asin, erf, sqrt
from statistics import median
from typing import Any, Callable, Iterable

import pandas as pd

from backend.research.historical_zone_performance import wilson_rate


TC_LABELS = (
    "VERY_HIGH",
    "HIGH",
    "MODERATE",
    "LOW",
    "CONFLICTED",
    "INSUFFICIENT_CONTEXT",
)


def reliability(sample_size: int) -> str:
    if sample_size < 30:
        return "INSUFFICIENT"
    if sample_size < 100:
        return "EXPLORATORY"
    if sample_size < 300:
        return "MODERATE_EVIDENCE"
    return "STRONGER_EVIDENCE"


def _median(rows: Iterable[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return round(median(values), 4) if values else None


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    interacted = [row for row in rows if row.get("entry_index") is not None]
    survived = sum(
        row.get("first_structural_failure_index") is None for row in interacted
    )
    targets = [row for row in interacted if row.get("target_price") is not None]
    target_hits = sum(row.get("first_target_index") is not None for row in targets)
    reactions = {
        str(level): sum((row.get("mfe_zone_width") or 0.0) >= level for row in interacted)
        for level in (0.5, 1, 2, 3, 5)
    }
    return {
        "detected": len(rows),
        "interacted": len(interacted),
        "reliability": reliability(len(interacted)),
        "interaction": wilson_rate(len(interacted), len(rows)).__dict__,
        "structural_survival": wilson_rate(survived, len(interacted)).__dict__,
        "reactions": {
            level: wilson_rate(count, len(interacted)).__dict__
            for level, count in reactions.items()
        },
        "target_available": len(targets),
        "target_achievement": wilson_rate(target_hits, len(targets)).__dict__,
        "median_mfe_zone_width": _median(interacted, "mfe_zone_width"),
        "median_mae_zone_width": _median(interacted, "mae_zone_width"),
    }


def group(
    rows: list[dict[str, Any]], key: Callable[[dict[str, Any]], str]
) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[key(row)].append(row)
    return {name: summarize(items) for name, items in sorted(grouped.items())}


def _rank_correlations(rows: list[dict[str, Any]], score_key: str) -> dict[str, Any]:
    interacted = [row for row in rows if row.get("entry_index") is not None]
    if len(interacted) < 2:
        return {}
    frame = pd.DataFrame(
        {
            "score": [row[score_key] for row in interacted],
            "reaction_1zw": [(row.get("mfe_zone_width") or 0) >= 1 for row in interacted],
            "reaction_2zw": [(row.get("mfe_zone_width") or 0) >= 2 for row in interacted],
            "reaction_3zw": [(row.get("mfe_zone_width") or 0) >= 3 for row in interacted],
            "mfe": [row.get("mfe_zone_width") for row in interacted],
            "survival": [
                row.get("first_structural_failure_index") is None for row in interacted
            ],
        }
    )
    result = {}
    for column in frame.columns:
        if column == "score" or frame[column].notna().sum() <= 1:
            continue
        if frame["score"].nunique(dropna=True) <= 1 or frame[column].nunique(dropna=True) <= 1:
            result[column] = None
            continue
        value = frame["score"].rank().corr(frame[column].rank())
        result[column] = None if pd.isna(value) else round(float(value), 4)
    return result


def _comparison(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "left": summarize(left),
        "right": summarize(right),
        "left_name": "HIGH_PLUS_VERY_HIGH",
        "right_name": "MODERATE",
    }
    for level in (1, 2, 3, 5):
        left_i = [row for row in left if row.get("entry_index") is not None]
        right_i = [row for row in right if row.get("entry_index") is not None]
        left_n = sum((row.get("mfe_zone_width") or 0) >= level for row in left_i)
        right_n = sum((row.get("mfe_zone_width") or 0) >= level for row in right_i)
        left_rate = wilson_rate(left_n, len(left_i))
        right_rate = wilson_rate(right_n, len(right_i))
        absolute = (
            None
            if left_rate.percent is None or right_rate.percent is None
            else round(left_rate.percent - right_rate.percent, 2)
        )
        relative = (
            None
            if right_rate.percent in (None, 0) or left_rate.percent is None
            else round(100 * (left_rate.percent / right_rate.percent - 1), 2)
        )
        effect = None
        p_value = None
        if left_i and right_i:
            p1 = left_n / len(left_i)
            p2 = right_n / len(right_i)
            effect = round(2 * (asin(sqrt(p1)) - asin(sqrt(p2))), 4)
            pooled = (left_n + right_n) / (len(left_i) + len(right_i))
            standard_error = sqrt(
                pooled * (1 - pooled) * (1 / len(left_i) + 1 / len(right_i))
            )
            if standard_error:
                z_score = (p1 - p2) / standard_error
                p_value = round(1 - erf(abs(z_score) / sqrt(2)), 6)
        result[f"reaction_{level}zw"] = {
            "absolute_percentage_points": absolute,
            "relative_percent": relative,
            "newcombe_ci_percentage_points": (
                None
                if left_rate.ci_low is None or right_rate.ci_high is None
                else [
                    round(left_rate.ci_low - right_rate.ci_high, 2),
                    round(left_rate.ci_high - right_rate.ci_low, 2),
                ]
            ),
            "cohen_h": effect,
            "two_proportion_p": p_value,
        }
    return result


def _context_class(row: dict[str, Any]) -> str:
    if row["tc_label"] == "CONFLICTED" or row["conflicted"]:
        return "CONFLICTED"
    if row["htf_compatibility"] == "ALIGNED" and row["trend_alignment"] == "ALIGNED":
        return "ALIGNED"
    return "NEUTRAL_OR_PARTIAL"


def _numeric_band(score: float) -> str:
    if score >= 85:
        return "85-100"
    if score >= 70:
        return "70-84.99"
    if score >= 50:
        return "50-69.99"
    return "0-49.99"


def _ranking(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["planning_timestamp"][:10], row["timeframe"])].append(row)
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    bucket_order = {
        "VERY_HIGH": 0,
        "HIGH": 1,
        "MODERATE": 2,
        "LOW": 5,
        "CONFLICTED": 6,
        "INSUFFICIENT_CONTEXT": 7,
    }
    cohort_count = 0
    for items in groups.values():
        if len(items) < 3:
            continue
        cohort_count += 1
        ordered = sorted(
            items,
            key=lambda row: (
                bucket_order[row["tc_label"]],
                -row["tc_score"],
                -row["zq_score"],
                row["zone_id"],
            ),
        )
        size = len(ordered)
        for index, row in enumerate(ordered):
            name = "TOP" if index < size / 3 else "MIDDLE" if index < 2 * size / 3 else "LOWER"
            buckets[name].append(row)
    return {
        "formation_cohorts": cohort_count,
        "limitation": (
            "Formation-time cohorts only; the replay does not contain every active "
            "Dashboard opportunity at every historical timestamp or the distance tie-breaker."
        ),
        "buckets": {name: summarize(items) for name, items in sorted(buckets.items())},
    }


def _cluster_key_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["symbol"], row["timeframe"], row["zone_type"], row["pattern"])].append(row)
    independent: list[dict[str, Any]] = []
    cluster_count = 0
    for items in grouped.values():
        items.sort(key=lambda row: row["planning_timestamp"])
        last: dict[str, Any] | None = None
        for row in items:
            if last is None:
                independent.append(row)
                last = row
                cluster_count += 1
                continue
            overlap = max(
                0.0,
                min(row["interaction_high"], last["interaction_high"])
                - max(row["interaction_low"], last["interaction_low"]),
            )
            timestamp = datetime.fromisoformat(row["planning_timestamp"])
            previous = datetime.fromisoformat(last["planning_timestamp"])
            maximum_days = 42 if row["timeframe"] == "1W" else 10
            if overlap > 0 and (timestamp - previous).days <= maximum_days:
                last = row
                continue
            independent.append(row)
            last = row
            cluster_count += 1
    return independent, cluster_count


def _leave_one_symbol_out(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def separation(items: list[dict[str, Any]]) -> float | None:
        high = [row for row in items if row["tc_label"] in {"HIGH", "VERY_HIGH"}]
        moderate = [row for row in items if row["tc_label"] == "MODERATE"]
        summary = _comparison(high, moderate)["reaction_2zw"]
        return summary["absolute_percentage_points"]

    overall = separation(rows)
    values = []
    symbols = sorted({row["symbol"] for row in rows})
    for symbol in symbols:
        value = separation([row for row in rows if row["symbol"] != symbol])
        if value is not None:
            values.append((symbol, value))
    return {
        "overall_high_plus_very_high_minus_moderate_2zw_pp": overall,
        "symbols_tested": len(values),
        "minimum": min(values, key=lambda item: item[1]) if values else None,
        "maximum": max(values, key=lambda item: item[1]) if values else None,
        "sign_reversals": sum(
            overall is not None and value * overall < 0 for _, value in values
        ),
        "sector_analysis": "UNAVAILABLE: no trustworthy frozen historical sector map was stored.",
    }


def analyze_shards(shards: list[dict[str, Any]]) -> dict[str, Any]:
    symbols: dict[str, dict[str, Any]] = {}
    for shard in shards:
        symbols.update(shard["symbols"])
    snapshots: dict[str, dict[str, Any]] = {}
    observations: dict[str, dict[str, Any]] = {}
    contexts: dict[str, dict[str, Any]] = {}
    for symbol in symbols.values():
        if symbol["status"] != "PROCESSED":
            continue
        snapshots.update({row["zone_id"]: row for row in symbol["snapshots"]})
        observations.update(
            {
                row["zone_id"]: row
                for row in symbol["observations"]
                if row.get("entry_policy") == "PROXIMAL"
            }
        )
        contexts.update({row["zone_id"]: row for row in symbol["contexts"]})

    zq_coverage: dict[str, int] = defaultdict(int)
    tc_coverage: dict[str, int] = defaultdict(int)
    rows: list[dict[str, Any]] = []
    for zone_id, snapshot in snapshots.items():
        context = contexts.get(zone_id)
        outcome = observations.get(zone_id)
        if context is None or outcome is None:
            zq_coverage["UNAVAILABLE"] += 1
            tc_coverage["UNAVAILABLE"] += 1
            continue
        zq = context["zone_quality"]
        tc = context["trade_confidence"]
        zq_coverage[zq["status"]] += 1
        tc_coverage[tc["status"]] += 1
        if zq["status"] != "AVAILABLE" or tc["status"] != "AVAILABLE":
            continue
        row = dict(snapshot)
        row.update(outcome)
        row.update(
            zq_score=float(zq["score"]),
            zq_label=zq["label"],
            tc_score=float(tc["score"]),
            tc_label=tc["label"],
            tc_sufficiency=tc["data_sufficiency"],
            conflicted=bool(tc["conflicted"]),
            htf_relationship=tc["htf_relationship"],
            htf_compatibility=tc["htf_compatibility"],
            trend_alignment=tc["trend_alignment"],
            zq_contribution=float(tc["zone_quality_contribution"]),
            htf_contribution=float(tc["htf_contribution"]),
            trend_contribution=float(tc["trend_contribution"]),
        )
        row["context_class"] = _context_class(row)
        row["planning_year"] = row["planning_timestamp"][:4]
        rows.append(row)

    labels = {
        label: summarize([row for row in rows if row["tc_label"] == label])
        for label in TC_LABELS
    }
    high = [row for row in rows if row["tc_label"] in {"HIGH", "VERY_HIGH"}]
    moderate = [row for row in rows if row["tc_label"] == "MODERATE"]
    independent, cluster_count = _cluster_key_rows(rows)
    ablation = {}
    for name, score in (
        ("A_ZONE_QUALITY", "zq_score"),
        ("B_ZQ_PLUS_HTF", "model_b"),
        ("C_ZQ_PLUS_TREND", "model_c"),
        ("D_FULL_TRADE_CONFIDENCE", "tc_score"),
    ):
        if score == "model_b":
            for row in rows:
                row[score] = row["zq_contribution"] + row["htf_contribution"]
        elif score == "model_c":
            for row in rows:
                row[score] = row["zq_contribution"] + row["trend_contribution"]
        ablation[name] = _rank_correlations(rows, score)

    failed = {
        name: {"error": value.get("error"), "message": value.get("message")}
        for name, value in symbols.items()
        if value["status"] != "PROCESSED"
    }
    zero_range = sum(
        int(value.get("zero_range_candles", 0))
        for value in symbols.values()
        if value["status"] == "PROCESSED"
    )
    first_dates = [
        series["first"]
        for value in symbols.values()
        if value["status"] == "PROCESSED"
        for series in value["series"]
        if series.get("first")
    ]
    last_dates = [
        series["last"]
        for value in symbols.values()
        if value["status"] == "PROCESSED"
        for series in value["series"]
        if series.get("last")
    ]
    timeframe_coverage: dict[str, dict[str, Any]] = {}
    for timeframe in ("1D", "1W"):
        matching = [
            series
            for value in symbols.values()
            if value["status"] == "PROCESSED"
            for series in value["series"]
            if series.get("timeframe", "1D") == timeframe
        ]
        timeframe_coverage[timeframe] = {
            "symbols": len(
                {
                    name
                    for name, value in symbols.items()
                    if value["status"] == "PROCESSED"
                    and any(series.get("timeframe", "1D") == timeframe for series in value["series"])
                }
            ),
            "segments": len(matching),
            "candles": sum(int(series.get("candles", 0)) for series in matching),
            "first": min((series["first"] for series in matching), default=None),
            "last": max((series["last"] for series in matching), default=None),
            "discovered": sum(int(series.get("discovered", 0)) for series in matching),
            "reconstructed": sum(int(series.get("reconstructed", 0)) for series in matching),
            "skipped": sum(int(series.get("skipped", 0)) for series in matching),
        }
    monotonicity = {}
    for metric in ("1", "2", "3", "5"):
        high_rate = labels["HIGH"]["reactions"][metric]["percent"]
        moderate_rate = labels["MODERATE"]["reactions"][metric]["percent"]
        low_rate = labels["LOW"]["reactions"][metric]["percent"]
        monotonicity[f"reaction_{metric}zw"] = {
            "high_gt_moderate": high_rate is not None and moderate_rate is not None and high_rate > moderate_rate,
            "moderate_gt_low": moderate_rate is not None and low_rate is not None and moderate_rate > low_rate,
            "very_high_comparison": "UNAVAILABLE: no VERY_HIGH observations",
        }
    for name, extractor in (
        ("target_achievement", lambda item: item["target_achievement"]["percent"]),
        ("structural_survival", lambda item: item["structural_survival"]["percent"]),
        ("median_mfe", lambda item: item["median_mfe_zone_width"]),
    ):
        high_value = extractor(labels["HIGH"])
        moderate_value = extractor(labels["MODERATE"])
        low_value = extractor(labels["LOW"])
        monotonicity[name] = {
            "high": high_value,
            "moderate": moderate_value,
            "low": low_value,
            "high_gt_moderate": high_value is not None and moderate_value is not None and high_value > moderate_value,
            "moderate_gt_low": moderate_value is not None and low_value is not None and moderate_value > low_value,
            "very_high_comparison": "UNAVAILABLE: no VERY_HIGH observations",
        }
    return {
        "dataset": {
            "requested_symbols": len(symbols),
            "processed_symbols": len(symbols) - len(failed),
            "failed_symbols": len(failed),
            "failed": failed,
            "total_canonical_zones": len(snapshots),
            "outcomes": len(observations),
            "trustworthy_records": len(rows),
            "first_usable_timestamp": min(first_dates) if first_dates else None,
            "last_usable_timestamp": max(last_dates) if last_dates else None,
            "zero_range_candles_skipped": zero_range,
            "universe_type": "CURRENT-CONSTITUENT HISTORICAL REPLAY",
            "timeframe_coverage": timeframe_coverage,
        },
        "coverage": {
            "zone_quality": dict(zq_coverage),
            "trade_confidence": dict(tc_coverage),
        },
        "table_b_tc_labels": labels,
        "table_c_tc_numeric_bands": group(rows, lambda row: _numeric_band(row["tc_score"])),
        "table_d_zone_quality": group(rows, lambda row: row["zq_label"]),
        "table_e_zq_x_tc": group(rows, lambda row: f"{row['zq_label']} x {row['tc_label']}"),
        "table_f_within_zq_context": group(rows, lambda row: f"{row['zq_label']} x {row['context_class']}"),
        "table_g_component_ablation": ablation,
        "table_h_htf": group(rows, lambda row: f"{row['htf_relationship']} x {row['htf_compatibility']}"),
        "table_i_trend": group(rows, lambda row: row["trend_alignment"]),
        "table_j_daily": group([row for row in rows if row["timeframe"] == "1D"], lambda row: row["tc_label"]),
        "table_k_weekly": group([row for row in rows if row["timeframe"] == "1W"], lambda row: row["tc_label"]),
        "table_l_zone_type": group(rows, lambda row: f"{row['zone_type']} x {row['tc_label']}"),
        "table_m_pattern": group(rows, lambda row: f"{row['pattern']} x {row['tc_label']}"),
        "table_n_year": group(rows, lambda row: f"{row['planning_year']} x {row['tc_label']}"),
        "table_o_dashboard_ranking": _ranking(rows),
        "table_p_symbol_robustness": _leave_one_symbol_out(rows),
        "table_q_cluster_sensitivity": {
            "definition": "Same symbol/timeframe/type/pattern, overlapping boundaries, and <=10 calendar days (Daily) or <=42 days (Weekly); retain earliest formation.",
            "raw": summarize(rows),
            "cluster_independent": summarize(independent),
            "clusters": cluster_count,
            "raw_tc_labels": labels,
            "cluster_tc_labels": group(independent, lambda row: row["tc_label"]),
        },
        "table_r_data_quality": {
            "failed_symbols": failed,
            "zero_range_candles_skipped": zero_range,
            "historical_constituents": "UNAVAILABLE",
            "sector_metadata": "UNAVAILABLE",
            "market_cap_metadata": "UNAVAILABLE",
            "corporate_action_note": "Provider data were adjusted by the existing provider path, but no immutable raw-versus-adjusted corporate-action ledger was stored; residual discontinuity risk remains.",
        },
        "major_comparison": _comparison(high, moderate),
        "monotonicity": monotonicity,
        "conflict_comparison": {
            "healthy_available": summarize([row for row in rows if row["tc_label"] not in {"CONFLICTED", "INSUFFICIENT_CONTEXT"}]),
            "conflicted": summarize([row for row in rows if row["tc_label"] == "CONFLICTED"]),
            "insufficient_context": summarize([row for row in rows if row["tc_label"] == "INSUFFICIENT_CONTEXT"]),
        },
        "correlations": {
            "zone_quality": _rank_correlations(rows, "zq_score"),
            "trade_confidence": _rank_correlations(rows, "tc_score"),
        },
    }
