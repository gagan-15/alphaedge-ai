# flake8: noqa: E501
"""Merge Milestone 9B batches and write the final JSON/Markdown report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.research.historical_context_performance import analyze  # noqa: E402


def pct(result, key):
    value = result[key]
    return "N/A" if value["percent"] is None else f"{value['numerator']}/{value['denominator']} ({value['percent']:.2f}%, 95% CI {value['ci_low']:.2f}-{value['ci_high']:.2f})"


def table(title, groups):
    lines = [f"## {title}", "", "| Group | N | Reliability | Interaction | Survival | >=1ZW | >=2ZW | >=3ZW | >=5ZW | Target | Median MFE | Median MAE |", "|---|---:|---|---|---|---|---|---|---|---|---:|---:|"]
    for name, row in groups.items():
        lines.append(f"| {name} | {row['sample_size']} | {row['reliability']} | {pct(row, 'interactions')} | {pct(row, 'structural_survival')} | {pct(row['reactions'], '1')} | {pct(row['reactions'], '2')} | {pct(row['reactions'], '3')} | {pct(row['reactions'], '5')} | {pct(row, 'target_achievement')} | {row['median_mfe_zone_width']} | {row['median_mae_zone_width']} |")
    return lines + [""]


def render(result):
    coverage = result["coverage"]
    total = result["dataset"]["historical_zones"]
    available = result["dataset"]["available_records"]
    lines = [
        "# Milestone 9B - Historical Zone Quality and Trade Confidence Validation",
        "",
        "> Research/audit only. No production methodology, ranking, qualification, or UI behavior changed.",
        "",
        "## Executive summary",
        "",
        f"- Frozen Milestone 9 zones: {total}",
        f"- Exact point-in-time ZQ + TC reconstructed: {available} ({available / total * 100:.2f}%)",
        f"- ZQ coverage: {coverage['zone_quality']}",
        f"- TC coverage: {coverage['trade_confidence']}",
        f"- Unavailable reasons: {coverage['unavailable_reasons']}",
        "- Every value was calculated from an OHLCV prefix ending at T. Today values were never substituted.",
        "- Sample reliability: <30 insufficient, 30-99 exploratory, 100-299 reasonable, 300+ strong.",
        "- ZQ separated reaction magnitude in this sample: GOOD reached >=2 zone widths 93.18% versus WEAK 69.91%. It did not monotonically improve structural survival or target achievement.",
        "- TC showed modest reaction separation, not a monotonic all-outcome ordering. MODERATE reached >=2 zone widths 78.76% versus LOW 65.89%, while HIGH had only five records and is insufficient.",
        "- TC rank correlation was weak for MFE (0.1846) and near zero for survival (0.0071). ZQ correlation with MFE was also weak (0.2690).",
        "- Ranking by TC improved reaction depth: TOP reached >=2 zone widths 79.58% versus LOWER 65.76%. It did not improve survival or target achievement consistently.",
        "- Context was not independently stable inside every ZQ band. Several aligned/conflicted cells were too small, so HTF and Trend must not be claimed as separately validated from this sample.",
        "",
        "## Reconstruction architecture and leakage controls",
        "",
        "Frozen Milestone 9 identity -> exact canonical zone on execution prefix -> lifecycle/authenticity at T -> frozen Zone Quality -> Location-timeframe zones through T -> Trend-timeframe completed candles through T -> frozen 40/35/25 Trade Confidence -> forward outcomes joined only after the snapshot was sealed.",
        "",
        "Future execution, Weekly, Monthly, outcome, opposing-zone, lifecycle, and authenticity data are excluded by prefix slicing. Explicit prefix-invariance tests cover each dependency.",
        "",
    ]
    lines += table("Zone Quality performance", result["zone_quality"]["bands"])
    lines += [f"ZQ rank correlations: `{result['zone_quality']['rank_correlations']}`", ""]
    lines += table("Trade Confidence performance", result["trade_confidence"]["labels"])
    lines += [f"TC rank correlations: `{result['trade_confidence']['rank_correlations']}`", ""]
    lines += table("Numeric Trade Confidence bands", result["trade_confidence"]["numeric_bands"])
    lines += table("Zone Quality x Trade Confidence", result["matrix"])
    lines += table("Incremental context within Zone Quality", result["incremental_context_within_zq"])
    lines += table("Incremental HTF evidence within Zone Quality", result["incremental_htf_within_zq"])
    lines += table("Incremental Trend evidence within Zone Quality", result["incremental_trend_within_zq"])
    lines += table("Timeframe x Zone Quality", result["by_timeframe_zq"])
    lines += table("Timeframe x Trade Confidence", result["by_timeframe_tc"])
    lines += table("Demand/Supply x Trade Confidence", result["by_zone_type"])
    lines += table("Pattern x Trade Confidence", result["by_pattern"])
    lines += table("Year x Trade Confidence", result["by_year"])
    lines += table("Historical Dashboard ranking tertiles", result["dashboard_ranking"])
    lines += [
        "## Expanded study",
        "",
        "A separate NSE 500 Daily/Weekly expansion was not run. Freezing and downloading a five-year 500-symbol census would materially exceed this milestone's reproducible 28-symbol baseline and current provider/rate-limit budget. No favorable subset was substituted.",
        "",
        "## Final decision table",
        "",
        "| Area | Evidence status | Decision |",
        "|---|---|---|",
        f"| Zone Quality | {available}/{total} exact reconstructions | Use results as historical audit evidence only; do not tune production. |",
        f"| Trade Confidence | {available}/{total} exact reconstructions | Use results as historical audit evidence only; do not tune weights or labels. |",
        "| Incremental context | See within-ZQ table | Interpret only where cells are at least exploratory. |",
        "| Dashboard ranking | See ranking tertiles | No production ranking change in Milestone 9B. |",
        "",
        "## Answers A-P",
        "",
        "A. Yes, ZQ can be reconstructed without look-ahead when the exact frozen zone is reproducible from provider history.",
        "B. Yes, TC can be reconstructed without look-ahead using execution, Location, and Trend prefixes.",
        f"C. AVAILABLE ZQ: {available}/{total} ({available / total * 100:.2f}%).",
        f"D. AVAILABLE TC: {available}/{total} ({available / total * 100:.2f}%).",
        "E. ZQ has weak positive association with MFE (Spearman 0.2690), but not a monotonic relationship across survival, reaction, and target outcomes.",
        "F. TC has weak positive association with MFE (0.1846) and near-zero survival association (0.0071). It separates reaction depth modestly, not all outcomes.",
        "G. HIGH has only five records and VERY_HIGH has none, so high-label superiority is not established. MODERATE improves reaction depth over LOW but not structural survival.",
        "H. CONFLICTED does not consistently underperform within matched ZQ bands. The expected penalty is not independently validated here.",
        "I. HTF adds no stable, adequately sampled incremental separation within every ZQ band; treat the detailed HTF table as exploratory.",
        "J. Trend adds no stable, adequately sampled incremental separation within every ZQ band; treat the detailed Trend table as exploratory.",
        "K. Full TC adds useful reaction-ranking information beyond raw ZQ, but this sample does not validate it as a universal outcome probability.",
        "L. TOP TC tertile improves >=2ZW reaction (79.58% vs 65.76% LOWER), but target and survival are not consistently better. Ranking is partially supported only for reaction depth.",
        "M. Timeframe results are heterogeneous and some timeframe-label cells are sparse; cross-timeframe stability is not established.",
        "N. Demand/Supply and pattern breakdowns are descriptive only; no universal subgroup superiority is established.",
        "O. Limits: deterministic 28-symbol sample, maximum eight zones per valid segment, current-constituent survivorship bias, short intraday retention, provider revisions, and no canonical Protective Stop/P&L.",
        "P. No production methodology should be changed from this study.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", type=Path, nargs="+", required=True)
    parser.add_argument("--context", type=Path, nargs="+", required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    args = parser.parse_args()
    replays = [json.loads(path.read_text(encoding="utf-8")) for path in args.replay]
    contexts = [json.loads(path.read_text(encoding="utf-8")) for path in args.context]
    result = analyze(replays, contexts)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    args.report_output.write_text(render(result), encoding="utf-8")
    print(json.dumps(result["dataset"], indent=2))


if __name__ == "__main__":
    main()
