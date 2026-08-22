# flake8: noqa: E501
"""Research-only aggregation for canonical historical zone performance.

This module consumes immutable point-in-time replay records.  It deliberately
does not import or alter any production scanner, scoring, ranking, or trading
methodology.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import sqrt
from statistics import median
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class Rate:
    numerator: int
    denominator: int
    percent: float | None
    ci_low: float | None
    ci_high: float | None


def wilson_rate(numerator: int, denominator: int) -> Rate:
    """Return a 95% Wilson interval; empty denominators stay explicit."""

    if denominator <= 0:
        return Rate(numerator, denominator, None, None, None)
    p = numerator / denominator
    z = 1.959963984540054
    denominator_term = 1 + z * z / denominator
    centre = (p + z * z / (2 * denominator)) / denominator_term
    margin = (
        z
        * sqrt((p * (1 - p) + z * z / (4 * denominator)) / denominator)
        / denominator_term
    )
    return Rate(
        numerator,
        denominator,
        round(100 * p, 2),
        round(100 * max(0.0, centre - margin), 2),
        round(100 * min(1.0, centre + margin), 2),
    )


def _median(values: Iterable[float | int | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    return round(median(clean), 4) if clean else None


def _first_per_zone(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Select one proximal observation per zone without stop-policy duplication."""

    selected: dict[str, dict[str, Any]] = {}
    for item in observations:
        if item.get("entry_policy") != "PROXIMAL":
            continue
        selected.setdefault(item["zone_id"], item)
    return list(selected.values())


def _summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    detected = len(records)
    interacted_rows = [item for item in records if item.get("entry_index") is not None]
    interacted = len(interacted_rows)
    survived = sum(
        item.get("first_structural_failure_index") is None for item in interacted_rows
    )
    thresholds = {
        str(level): sum(
            (item.get("mfe_zone_width") or 0.0) >= level for item in interacted_rows
        )
        for level in (0.5, 1, 2, 3, 5)
    }
    target_rows = [
        item for item in interacted_rows if item.get("target_price") is not None
    ]
    target_hit = sum(item.get("first_target_index") is not None for item in target_rows)
    target_before_failure = sum(
        item.get("first_target_index") is not None
        and (
            item.get("first_structural_failure_index") is None
            or item["first_target_index"] < item["first_structural_failure_index"]
        )
        for item in target_rows
    )
    failure_before_target = sum(
        item.get("first_structural_failure_index") is not None
        and (
            item.get("first_target_index") is None
            or item["first_structural_failure_index"] < item["first_target_index"]
        )
        for item in target_rows
    )
    same_candle = sum(
        item.get("first_target_index") is not None
        and item.get("first_target_index") == item.get("first_structural_failure_index")
        for item in target_rows
    )
    unresolved = (
        len(target_rows) - target_before_failure - failure_before_target - same_candle
    )
    return {
        "detected": detected,
        "interacted": interacted,
        "never_interacted": detected - interacted,
        "interaction_rate": wilson_rate(interacted, detected),
        "structural_survival": wilson_rate(survived, interacted),
        "failure": wilson_rate(interacted - survived, interacted),
        "reaction_rates": {
            level: wilson_rate(count, interacted) for level, count in thresholds.items()
        },
        "target_available": len(target_rows),
        "target_achievement": wilson_rate(target_hit, len(target_rows)),
        "target_before_failure": wilson_rate(target_before_failure, len(target_rows)),
        "failure_before_target": wilson_rate(failure_before_target, len(target_rows)),
        "same_candle_ambiguous": same_candle,
        "unresolved": unresolved,
        "median_mfe_zone_width": _median(
            item.get("mfe_zone_width") for item in interacted_rows
        ),
        "median_mae_zone_width": _median(
            item.get("mae_zone_width") for item in interacted_rows
        ),
        "median_mfe_atr": _median(item.get("mfe_atr") for item in interacted_rows),
        "median_mae_atr": _median(item.get("mae_atr") for item in interacted_rows),
        "median_candles_to_interaction": _median(
            item.get("candles_to_entry") for item in interacted_rows
        ),
    }


def _group(
    records: list[dict[str, Any]], key: Callable[[dict[str, Any]], str]
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[key(record)].append(record)
    return {name: _summarize(group) for name, group in sorted(groups.items())}


def analyze_replay(payload: dict[str, Any]) -> dict[str, Any]:
    """Build transparent Milestone 9 metrics from one replay payload."""

    snapshots = {item["zone_id"]: item for item in payload["snapshots"]}
    records = _first_per_zone(payload["observations"])
    for record in records:
        snapshot = snapshots[record["zone_id"]]
        record["planning_timestamp"] = snapshot["planning_timestamp"]
        record["lifecycle_at_t"] = snapshot["selected_lifecycle_status"]
        record["authenticity_at_t"] = snapshot["selected_authenticity_status"]
    result = {
        "dataset": payload["dataset"],
        "overall": _summarize(records),
        "by_timeframe": _group(records, lambda item: item["timeframe"]),
        "by_zone_type": _group(records, lambda item: item["zone_type"]),
        "by_pattern": _group(records, lambda item: item["pattern"]),
        "by_lifecycle": _group(records, lambda item: item["lifecycle_at_t"]),
        "by_year": _group(records, lambda item: str(item["planning_timestamp"])[:4]),
        "by_symbol": _group(records, lambda item: item["symbol"]),
        "data_quality": {
            "series_requested": payload["dataset"].get("series_requested"),
            "series_succeeded": payload["dataset"].get("series_succeeded"),
            "series_failed": payload["dataset"].get("series_failed"),
            "reconstruction_failures": len(payload.get("failures", [])),
            "limitations": payload.get("limitations", []),
        },
        "excluded_metrics": {
            "zone_quality": "The frozen replay did not store point-in-time Zone Quality.",
            "trade_confidence": "The frozen replay did not store point-in-time HTF, Trend, or Trade Confidence.",
            "zone_quality_x_trade_confidence": "Required point-in-time fields are unavailable.",
            "market_regime": "No frozen research-only regime definition was present.",
            "failure_before_reaction": "Threshold crossing timestamps were not stored; later MFE cannot be used without leakage.",
        },
    }
    return result
