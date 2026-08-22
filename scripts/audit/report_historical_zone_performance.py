# flake8: noqa: E501
"""Generate the Milestone 9 report from an immutable point-in-time replay."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from backend.research.historical_zone_performance import Rate, analyze_replay


def _rate(value: Rate | dict[str, Any]) -> str:
    if isinstance(value, dict):
        value = Rate(**value)
    if value.percent is None:
        return "N/A"
    return (
        f"{value.numerator}/{value.denominator} ({value.percent:.2f}%; "
        f"95% CI {value.ci_low:.2f}–{value.ci_high:.2f})"
    )


def _table(title: str, groups: dict[str, dict[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Group | Zones | Interacted | Survival | >=1ZW | >=2ZW | >=3ZW | Target reached | Median MFE (ZW) | Median MAE (ZW) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in groups.items():
        lines.append(
            "| {name} | {detected} | {interacted} | {survival} | {r1} | {r2} | {r3} | {target} | {mfe} | {mae} |".format(
                name=name,
                detected=row["detected"],
                interacted=row["interacted"],
                survival=_rate(row["structural_survival"]),
                r1=_rate(row["reaction_rates"]["1"]),
                r2=_rate(row["reaction_rates"]["2"]),
                r3=_rate(row["reaction_rates"]["3"]),
                target=_rate(row["target_achievement"]),
                mfe=row["median_mfe_zone_width"],
                mae=row["median_mae_zone_width"],
            )
        )
    lines.append("")
    return lines


def render(result: dict[str, Any]) -> str:
    overall = result["overall"]
    dataset = result["dataset"]
    lines = [
        "# Milestone 9 — Canonical Historical Zone Performance Validation",
        "",
        "> Research/audit only. No production methodology or behavior changed.",
        "",
        "## Executive Summary",
        "",
        f"- Period: {dataset['date_start']} to {dataset['date_end']}",
        f"- Universe: {dataset['symbols_requested']} frozen deterministic NSE symbols ({dataset['series_succeeded']}/{dataset['series_requested']} series succeeded)",
        "- Timeframes: 15m, 75m, 125m, Daily, Weekly",
        f"- Point-in-time reconstructed zones: {overall['detected']}",
        f"- Interacted: {_rate(overall['interaction_rate'])}",
        f"- Never interacted: {overall['never_interacted']}",
        f"- Structural survival among interacted zones: {_rate(overall['structural_survival'])}",
        f"- >=1 zone-width reaction: {_rate(overall['reaction_rates']['1'])}",
        f"- >=2 zone-width reaction: {_rate(overall['reaction_rates']['2'])}",
        f"- >=3 zone-width reaction: {_rate(overall['reaction_rates']['3'])}",
        f"- >=5 zone-width reaction: {_rate(overall['reaction_rates']['5'])}",
        f"- Structural target reached where available: {_rate(overall['target_achievement'])}",
        "",
        "## Scope and reliability",
        "",
        "This is a deterministic, history-spanning validation sample, not a complete NSE 500 census. The frozen replay sampled at most eight zones per valid data segment. Daily and Weekly data cover the five-year target window; Yahoo intraday retention is shorter, so intraday rows do not represent five full years. Current NSE constituents were used, so survivorship bias remains. No profit, win-rate, CAGR, Sharpe, position sizing, protective-stop, or P&L claim is made.",
        "",
        "Reporting rule: fewer than 30 observations is descriptive only; 30–99 supports cautious directional reading; 100+ supports stronger descriptive conclusions. These are reporting safeguards, not production thresholds.",
        "",
    ]
    lines += _table("Table A — Overall historical performance", {"All zones": overall})
    lines += _table("Table B — Performance by timeframe", result["by_timeframe"])
    lines += _table("Table C — Demand vs Supply", result["by_zone_type"])
    lines += _table("Table D — Pattern performance", result["by_pattern"])
    lines += [
        "## Table E — Zone Quality bands",
        "",
        "Excluded: point-in-time Zone Quality was not stored in the frozen replay. Reconstructing it from a later snapshot would violate the no-look-ahead rule.",
        "",
    ]
    lines += [
        "## Table F — Trade Confidence labels",
        "",
        "Excluded: point-in-time HTF Location, Trend and Trade Confidence were not stored. No values were fabricated.",
        "",
    ]
    lines += [
        "## Table G — Zone Quality x Trade Confidence",
        "",
        "Excluded because both point-in-time dimensions are unavailable.",
        "",
    ]
    lines += _table(
        "Table H — Fresh vs Tested at planning time", result["by_lifecycle"]
    )
    lines += _table("Table I — Year-by-year", result["by_year"])
    lines += _table("Table J — Structural plan outcomes", {"Plans": overall})
    lines += _table("Table K — Symbol robustness", result["by_symbol"])
    dq = result["data_quality"]
    lines += [
        "## Table L — Data quality and exclusions",
        "",
        "| Item | Result |",
        "|---|---|",
        f"| Requested series | {dq['series_requested']} |",
        f"| Successful series | {dq['series_succeeded']} |",
        f"| Failed series | {dq['series_failed']} |",
        f"| Reconstruction failures | {dq['reconstruction_failures']} |",
        "| Provider | YahooProvider |",
        "| Corporate actions | Provider-adjusted history; independent corporate-action audit unavailable |",
        "| Historical membership | Unavailable; current-constituent survivorship bias remains |",
        "| Intraday history | Provider retention shorter than five years |",
        "| Complete-zone census | No; maximum eight zones per valid segment |",
        "",
        "## Direct answers",
        "",
        f"A. The frozen sample reconstructed {overall['detected']} canonical zones; this is not the total five-year NSE 500 count.",
        f"B. {_rate(overall['interaction_rate'])} interacted within the frozen horizon.",
        f"C. {_rate(overall['structural_survival'])} of interacted zones structurally survived.",
        f"D. >=1ZW {_rate(overall['reaction_rates']['1'])}; >=2ZW {_rate(overall['reaction_rates']['2'])}; >=3ZW {_rate(overall['reaction_rates']['3'])}; >=5ZW {_rate(overall['reaction_rates']['5'])}.",
        f"E. {_rate(overall['target_achievement'])} reached the structural target where a point-in-time target existed.",
        "F–H. Demand/Supply, pattern and timeframe comparisons are shown in Tables B–D; small samples must be treated cautiously.",
        "I–L. Zone Quality and Trade Confidence predictive ordering cannot be answered from this frozen replay without look-ahead leakage; they are explicitly excluded.",
        "M. Year stability is shown in Table I, with partial 2021 and 2026 periods.",
        "N. Symbol dispersion is shown in Table K. The deterministic 28-symbol sample is too small for an NSE-wide robustness claim.",
        "O. Main uncertainty: current-constituent survivorship bias, limited intraday history, sampled zones, provider-adjusted corporate actions, and missing point-in-time ZQ/TC context.",
        "P. The sample provides descriptive evidence about structural zone behavior, but it is not sufficient for a final claim about the complete AlphaEdge methodology.",
        "Q. Formation/lifecycle/structural-plan behavior can be evaluated here. ZQ and TC predictive power remain unvalidated until a new replay stores those fields at T.",
        "",
        "## Point-in-time controls",
        "",
        "Zones were first discovered for audit indexing, then reconstructed from a candle prefix ending at the historical planning timestamp. Lifecycle, authenticity and opposing targets were computed from that prefix. Later candles were exposed only to outcome observation. Any metric not frozen at T was excluded rather than backfilled.",
        "",
        "## Production impact",
        "",
        "None. This report and its aggregation utilities are isolated research artifacts. Frozen Formation V1.1, boundaries, lifecycle, authenticity, Zone Quality, HTF Location, Trend, Trade Confidence, Dashboard qualification, ranking and Trade Planning V1 were not changed.",
    ]
    return "\n".join(lines) + "\n"


def merge_payloads(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge independent deterministic replay batches without hiding failures."""

    if len(payloads) == 1:
        return payloads[0]
    base = payloads[0]
    snapshots = [item for payload in payloads for item in payload["snapshots"]]
    observations = [item for payload in payloads for item in payload["observations"]]
    canonical_timeframes = {"15m", "75m", "125m", "1D", "1W"}
    failures = [
        item
        for payload in payloads
        for item in payload.get("failures", [])
        if item.get("timeframe") in canonical_timeframes
    ]
    limitations = sorted(
        {item for payload in payloads for item in payload.get("limitations", [])}
    )
    starts = [payload["dataset"]["date_start"] for payload in payloads]
    ends = [payload["dataset"]["date_end"] for payload in payloads]
    dataset = dict(base["dataset"])
    represented_timeframes = {item["timeframe"] for item in snapshots} | {
        item["timeframe"] for item in failures
    }
    requested_series = dataset["symbols_requested"] * len(represented_timeframes)
    dataset.update(
        series_requested=requested_series,
        series_succeeded=requested_series - len(failures),
        series_failed=len(failures),
        zones_reconstructed=len(snapshots),
        date_start=min(starts),
        date_end=max(ends),
    )
    return {
        "audit": {
            "name": "MILESTONE_9_CANONICAL_ZONE_PERFORMANCE_REPLAY",
            "production_activation": False,
            "batches": len(payloads),
        },
        "dataset": dataset,
        "snapshots": snapshots,
        "observations": observations,
        "failures": failures,
        "limitations": limitations,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, nargs="+")
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    args = parser.parse_args()
    payload = merge_payloads(
        [json.loads(path.read_text(encoding="utf-8")) for path in args.input]
    )
    result = analyze_replay(payload)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(result, default=lambda value: value.__dict__, indent=2),
        encoding="utf-8",
    )
    args.report_output.write_text(render(result), encoding="utf-8")


if __name__ == "__main__":
    main()
