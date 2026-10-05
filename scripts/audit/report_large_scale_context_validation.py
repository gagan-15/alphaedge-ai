#!/usr/bin/env python
# flake8: noqa: E402,E501
"""Generate the frozen Milestone 9C evidence report from completed shards."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.research.large_scale_context_performance import TC_LABELS, analyze_shards


def _pct(rate: dict[str, Any]) -> str:
    if rate.get("percent") is None:
        return "—"
    return f"{rate['percent']:.2f}% [{rate['ci_low']:.2f}, {rate['ci_high']:.2f}]"


def _metric_table(title: str, groups: dict[str, dict[str, Any]]) -> list[str]:
    lines = [f"## {title}", "", "| Group | N | Interacted | Interaction | Survival | >=1ZW | >=2ZW | >=3ZW | >=5ZW | Target N | Target achieved | Median MFE | Median MAE | Evidence |", "|---|---:|---:|---|---|---|---|---|---|---:|---|---:|---:|---|"]
    for name, row in groups.items():
        reaction = row["reactions"]
        lines.append(
            f"| {name} | {row['detected']} | {row['interacted']} | {_pct(row['interaction'])} | "
            f"{_pct(row['structural_survival'])} | {_pct(reaction['1'])} | {_pct(reaction['2'])} | "
            f"{_pct(reaction['3'])} | {_pct(reaction['5'])} | {row['target_available']} | "
            f"{_pct(row['target_achievement'])} | {row['median_mfe_zone_width'] or '—'} | "
            f"{row['median_mae_zone_width'] or '—'} | {row['reliability']} |"
        )
    return lines + [""]


def _simple_table(title: str, rows: dict[str, Any]) -> list[str]:
    lines = [f"## {title}", "", "| Item | Result |", "|---|---|"]
    for key, value in rows.items():
        display = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
        safe_display = display.replace("|", "\\|")
        lines.append(f"| {key} | {safe_display} |")
    return lines + [""]


def _rate(groups: dict[str, Any], label: str, level: str) -> float | None:
    return groups.get(label, {}).get("reactions", {}).get(level, {}).get("percent")


def _yes_no(left: float | None, right: float | None) -> str:
    if left is None or right is None:
        return "INCONCLUSIVE"
    return "YES" if left > right else "NO"


def _answers(result: dict[str, Any]) -> list[tuple[str, str]]:
    labels = result["table_b_tc_labels"]
    high_n = labels["HIGH"]["interacted"] + labels["VERY_HIGH"]["interacted"]
    high_2 = result["major_comparison"]["left"]["reactions"]["2"]["percent"]
    moderate_2 = result["major_comparison"]["right"]["reactions"]["2"]["percent"]
    low_2 = _rate(labels, "LOW", "2")
    conflicted_2 = _rate(labels, "CONFLICTED", "2")
    healthy_2 = result["conflict_comparison"]["healthy_available"]["reactions"]["2"]["percent"]
    zq_corr = result["correlations"]["zone_quality"].get("reaction_2zw")
    tc_corr = result["correlations"]["trade_confidence"].get("reaction_2zw")
    ablation = result["table_g_component_ablation"]
    best = max(
        ablation,
        key=lambda name: ablation[name].get("reaction_2zw") or -999,
    )
    ranking = result["table_o_dashboard_ranking"]["buckets"]
    top_2 = ranking.get("TOP", {}).get("reactions", {}).get("2", {}).get("percent")
    lower_2 = ranking.get("LOWER", {}).get("reactions", {}).get("2", {}).get("percent")
    data = result["dataset"]
    coverage = result["coverage"]
    return [
        ("A", f"{data['total_canonical_zones']} Daily/Weekly canonical zones."),
        ("B", f"{coverage['zone_quality'].get('AVAILABLE', 0)} had exact point-in-time ZQ."),
        ("C", f"{coverage['trade_confidence'].get('AVAILABLE', 0)} had exact point-in-time TC records."),
        ("D", f"{labels['VERY_HIGH']['detected']} VERY_HIGH records."),
        ("E", f"{labels['HIGH']['detected']} HIGH records."),
        ("F", f"{'YES' if high_n >= 100 else 'NO'}; interacted HIGH+VERY_HIGH N={high_n}, evidence={labels['HIGH']['reliability']}."),
        ("G", f"{_yes_no(_rate(labels, 'VERY_HIGH', '2'), _rate(labels, 'HIGH', '2'))} for >=2ZW; see Table B for all outcomes and uncertainty."),
        ("H", f"{_yes_no(_rate(labels, 'HIGH', '2'), moderate_2)} for >=2ZW."),
        ("I", f"{_yes_no(high_2, moderate_2)} for >=2ZW; difference={result['major_comparison']['reaction_2zw']['absolute_percentage_points']} pp."),
        ("J", f"{_yes_no(moderate_2, low_2)} for >=2ZW."),
        ("K", f"{_yes_no(healthy_2, conflicted_2)}: healthy available >=2ZW={healthy_2}%, conflicted={conflicted_2}%."),
        ("L", f"ZQ Spearman association with >=2ZW={zq_corr}; direction and band tables show the observed separation."),
        ("M", "See Table F/H. Within-ZQ results are observational and do not establish independent causal value."),
        ("N", "See Table F/I. Within-ZQ results are observational and do not establish independent causal value."),
        ("O", f"The strongest observed >=2ZW ordering was {best}; full TC correlation={tc_corr}, so incremental value is reported descriptively, not assumed."),
        ("P", "See Table B target-achievement rates; availability is structural and uneven, so evidence is conditional."),
        ("Q", "See Table B structural-survival rates and Wilson intervals."),
        ("R", "Compare reaction-depth separation with survival separation in Table B; no trading-win interpretation is made."),
        ("S", f"{'LIMITED SUPPORT' if top_2 is not None and lower_2 is not None and top_2 > lower_2 else 'NOT SUPPORTED/INCONCLUSIVE'} in formation cohorts; this is not a complete active-Dashboard replay."),
        ("T", "See Tables J/K; Weekly conclusions must follow its smaller sample and intervals."),
        ("U", "See Table L; consistency is assessed separately for Demand and Supply."),
        ("V", "See Table M; no pattern-specific tuning was performed."),
        ("W", "See Table N; partial 2021/2026 and regime differences limit stability claims."),
        ("X", f"Leave-one-symbol-out sign reversals={result['table_p_symbol_robustness']['sign_reversals']}; sector robustness is unavailable without trustworthy frozen metadata."),
        ("Y", "Current-constituent survivorship bias, one malformed-symbol exclusion, provider adjustment uncertainty, data breaks, incomplete sector/market-cap metadata, and formation-cohort ranking proxy remain."),
        ("Z", "NO. Milestone 9C is research evidence only; no production methodology change is approved."),
    ]


def _report(result: dict[str, Any], manifest: dict[str, Any]) -> str:
    labels = result["table_b_tc_labels"]
    data = result["dataset"]
    coverage = result["coverage"]
    lines = [
        "# Milestone 9C — Large-Scale Daily/Weekly Trade Confidence Validation",
        "",
        "> Research/audit only. Historical reactions are not trade wins, and Trade Confidence is not a probability of profit.",
        "",
        "## Executive summary",
        "",
        f"- Universe: frozen current NSE 500 constituent file ({data['requested_symbols']} requested; {data['processed_symbols']} processed; {data['failed_symbols']} excluded)",
        f"- Period: {data['first_usable_timestamp']} to {data['last_usable_timestamp']} where provider history permitted",
        f"- Total canonical zones: {data['total_canonical_zones']}",
        f"- ZQ available: {coverage['zone_quality'].get('AVAILABLE', 0)}",
        f"- TC available: {coverage['trade_confidence'].get('AVAILABLE', 0)}",
        "- Replay label: CURRENT-CONSTITUENT HISTORICAL REPLAY (historical membership unavailable)",
        "",
        "### TC distribution",
        "",
    ]
    for label in TC_LABELS:
        lines.append(f"- {label}: {labels[label]['detected']} detected / {labels[label]['interacted']} interacted")
    lines += ["", "### Key reaction evidence", ""]
    for level in ("2", "3"):
        lines.append(f"**>={level} Zone-Width Reaction**")
        for label in ("VERY_HIGH", "HIGH", "MODERATE", "LOW", "CONFLICTED"):
            lines.append(f"- {label}: {_pct(labels[label]['reactions'][level])}")
        lines.append("")
    lines.append("**Structural Target Achievement**")
    for label in ("VERY_HIGH", "HIGH", "MODERATE", "LOW", "CONFLICTED"):
        lines.append(f"- {label}: {_pct(labels[label]['target_achievement'])}")
    comparison = result["major_comparison"]["reaction_2zw"]
    lines += [
        "",
        "### Direct conclusions",
        "",
        f"- HIGH+VERY_HIGH versus MODERATE >=2ZW: {comparison['absolute_percentage_points']} percentage points; Newcombe interval {comparison['newcombe_ci_percentage_points']}; Cohen h {comparison['cohen_h']}.",
        "- No VERY_HIGH observations were available, so VERY_HIGH cannot be validated or compared with HIGH.",
        "- HIGH evidence is almost entirely Daily; Weekly HIGH evidence is insufficient.",
        "- Overall ablation did not show incremental rank association beyond Zone Quality: full Trade Confidence was slightly lower than Zone Quality alone for >=2ZW.",
        "- Within fixed Zone Quality bands, aligned context often performed better than conflicted context. This is observational support, not approval to retune weights.",
        "- Dashboard ranking supported deeper reactions, but not better structural survival or target achievement; it was a formation-cohort proxy, not a complete active-opportunity replay.",
        "- Cluster sensitivity and leave-one-symbol-out checks did not overturn the main HIGH versus MODERATE reaction-depth result.",
        "",
        "## Replay architecture and leakage lock",
        "",
        "The runner froze the 500-symbol file and checksum before outcomes, fetched one Daily provider series per symbol, derived Weekly/Monthly context locally, split invalid-candle continuity breaks, enumerated all canonical formations without an eight-zone cap, and reconstructed every zone from candles available at or before its formation timestamp. Per-symbol atomic checkpoints make the run restartable. No outcome influenced selection or context reconstruction.",
        "",
        "The optimized research path detects each execution/location series once, then applies the same canonical known-at-time filtering before reconstructing lifecycle, authenticity, ZQ, HTF, Trend, and frozen 40/35/25 TC. Future-candle invariance and equivalence are regression-tested.",
        "",
    ]
    lines += _simple_table("Table A — Dataset / coverage", {**data, **coverage, **manifest})
    lines += _metric_table("Table B — Trade Confidence labels", result["table_b_tc_labels"])
    lines += _metric_table("Table C — Trade Confidence numeric bands", result["table_c_tc_numeric_bands"])
    lines += _metric_table("Table D — Zone Quality", result["table_d_zone_quality"])
    lines += _metric_table("Table E — ZQ x TC", result["table_e_zq_x_tc"])
    lines += _metric_table("Table F — Within-ZQ context comparison", result["table_f_within_zq_context"])
    lines += _simple_table("Table G — Component ablation (Spearman rank associations)", result["table_g_component_ablation"])
    lines += _metric_table("Table H — HTF relationship / compatibility", result["table_h_htf"])
    lines += _metric_table("Table I — Trend alignment", result["table_i_trend"])
    lines += _metric_table("Table J — Daily Trade Confidence", result["table_j_daily"])
    lines += _metric_table("Table K — Weekly Trade Confidence", result["table_k_weekly"])
    lines += _metric_table("Table L — Demand vs Supply", result["table_l_zone_type"])
    lines += _metric_table("Table M — Pattern results", result["table_m_pattern"])
    lines += _metric_table("Table N — Year-by-year", result["table_n_year"])
    lines += _simple_table("Table O — Dashboard ranking replay", result["table_o_dashboard_ranking"])
    lines += _simple_table("Table P — Symbol / sector robustness", result["table_p_symbol_robustness"])
    lines += _simple_table("Table Q — Duplicate / cluster sensitivity", result["table_q_cluster_sensitivity"])
    lines += _simple_table("Table R — Data quality / exclusions", result["table_r_data_quality"])
    lines += [
        "## Major comparisons and limitations",
        "",
        "```json",
        json.dumps({"high_plus_very_high_vs_moderate": result["major_comparison"], "conflict": result["conflict_comparison"], "correlations": result["correlations"]}, indent=2, sort_keys=True),
        "```",
        "",
        "## Monotonicity checks",
        "",
        "```json",
        json.dumps(result["monotonicity"], indent=2, sort_keys=True),
        "```",
        "",
        "## Answers A–Z",
        "",
    ]
    for letter, answer in _answers(result):
        lines.append(f"- **{letter}.** {answer}")
    lines += [
        "",
        "## Interpretation guardrails",
        "",
        "- This is historical reaction research, not a backtested executable strategy.",
        "- No stop-loss, position sizing, trading P&L, BUY/SELL label, or win rate was introduced.",
        "- The NSE 500 file is today's known membership, so delisted/removed historical constituents are absent and survivorship bias remains.",
        "- CHENNPETRO was excluded because provider OHLC was internally malformed; its values were not repaired.",
        "- No production formula, threshold, label, ranking, qualification, recommendation, or UI behavior changed.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shards", nargs="+", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--report-output", required=True)
    args = parser.parse_args()
    paths = [Path(value) for value in args.shards]
    shards = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    result = analyze_shards(shards)
    result["dataset"]["last_usable_timestamp"] = shards[0]["audit"]["period_end"]
    manifest = {
        "shard_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
        },
        "universe_sha256": shards[0]["audit"]["universe_checksum"],
        "period_start": shards[0]["audit"]["period_start"],
        "period_end": shards[0]["audit"]["period_end"],
        "deterministic_policy": "All canonical 1D/1W zones; no outcome-based sampling or cap.",
    }
    output = {"manifest": manifest, "analysis": result}
    Path(args.json_output).write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    Path(args.report_output).write_text(_report(result, manifest), encoding="utf-8")


if __name__ == "__main__":
    main()
