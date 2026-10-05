"""Build the frozen cross-timeframe Leg-In structural study."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

FIXTURE_DIR = Path("tests/fixtures/leg_in_structural")
TARGET = FIXTURE_DIR / "multitimeframe_summary.json"
REVIEW_TARGET = FIXTURE_DIR / "human_review_set.json"
DATASETS = (
    "daily_nse500.json",
    "weekly_nifty100.json",
    "minute_15_nifty50.json",
    "minute_75_nifty50.json",
    "minute_125_nifty50.json",
)
RULES = {
    "HARD_WIDTH_050": lambda item: item["displacement_zone_width_ratio"] >= 0.50,
    "HARD_WIDTH_100": lambda item: item["displacement_zone_width_ratio"] >= 1.00,
    "HARD_VOLATILITY_075": lambda item: (
        item["displacement_volatility_ratio"] is not None
        and item["displacement_volatility_ratio"] >= 0.75
    ),
    "HARD_VOLATILITY_100": lambda item: (
        item["displacement_volatility_ratio"] is not None
        and item["displacement_volatility_ratio"] >= 1.00
    ),
    "HARD_OCCUPANCY_080": lambda item: item["prior_zone_occupancy_ratio"] <= 0.80,
    "HARD_OCCUPANCY_065": lambda item: item["prior_zone_occupancy_ratio"] <= 0.65,
    "HARD_OVERLAP_080": lambda item: item["approach_overlap_ratio"] <= 0.80,
    "COMBINED_LENIENT": lambda item: (
        item["displacement_zone_width_ratio"] >= 0.50
        and not (
            item["prior_zone_occupancy_ratio"] > 0.80
            and item["approach_overlap_ratio"] > 0.80
            and item["directional_efficiency"] < 0.65
        )
    ),
    "COMBINED_BALANCED": lambda item: (
        item["displacement_zone_width_ratio"] >= 0.50
        and not (
            item["prior_zone_occupancy_ratio"] > 0.80
            and (
                item["approach_overlap_ratio"] > 0.70
                or item["directional_efficiency"] < 0.50
            )
        )
    ),
    "TIERED_MINIMUM": lambda item: item["structural_state"]
    not in {"CONGESTED", "INSUFFICIENT_EVIDENCE"},
}


def _impact(records: list[dict[str, Any]], predicate) -> dict[str, Any]:
    kept = [item for item in records if predicate(item)]
    removed = [item for item in records if not predicate(item)]

    def breakdown(items, key, values):
        return {value: sum(item[key] == value for item in items) for value in values}

    return {
        "retained": len(kept),
        "rejected": len(removed),
        "dashboard_retained": sum(item["dashboard_visible"] for item in kept),
        "dashboard_rejected": sum(item["dashboard_visible"] for item in removed),
        "one_candle_retained": sum(item["leg_in_candle_count"] == 1 for item in kept),
        "one_candle_rejected": sum(
            item["leg_in_candle_count"] == 1 for item in removed
        ),
        "multi_candle_retained": sum(item["leg_in_candle_count"] > 1 for item in kept),
        "multi_candle_rejected": sum(
            item["leg_in_candle_count"] > 1 for item in removed
        ),
        "patterns_retained": breakdown(kept, "pattern", ("DBR", "RBR", "RBD", "DBD")),
        "patterns_rejected": breakdown(
            removed, "pattern", ("DBR", "RBR", "RBD", "DBD")
        ),
        "types_retained": breakdown(kept, "zone_type", ("DEMAND", "SUPPLY")),
        "types_rejected": breakdown(removed, "zone_type", ("DEMAND", "SUPPLY")),
        "timeframes_retained": dict(Counter(item["timeframe"] for item in kept)),
        "timeframes_rejected": dict(Counter(item["timeframe"] for item in removed)),
    }


def _example(records, state, direction, multi=None):
    patterns = {"DROP": {"DBR", "DBD"}, "RALLY": {"RBR", "RBD"}}[direction]
    candidates = [
        item
        for item in records
        if item["structural_state"] == state and item["pattern"] in patterns
    ]
    if multi is not None:
        candidates = [
            item for item in candidates if (item["leg_in_candle_count"] > 1) == multi
        ]
    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            not item["dashboard_visible"],
            -item["directional_efficiency"],
            item["prior_zone_occupancy_ratio"],
        )
    )
    return candidates[0]


def main() -> None:
    datasets = []
    records = []
    for name in DATASETS:
        payload = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
        datasets.append(
            {key: payload[key] for key in payload if key not in {"records", "failures"}}
        )
        records.extend(payload["records"])
    sonacoms = [
        item
        for item in records
        if item["symbol"] == "SONACOMS"
        and abs(item["proximal"] - 720.5) < 0.02
        and abs(item["distal"] - 707.0) < 0.02
    ]
    examples = {
        "clean_one_candle_drop": _example(records, "CLEAN", "DROP", False),
        "clean_one_candle_rally": _example(records, "CLEAN", "RALLY", False),
        "clean_multi_candle_drop": _example(records, "CLEAN", "DROP", True),
        "clean_multi_candle_rally": _example(records, "CLEAN", "RALLY", True),
        "congested_drop": _example(records, "CONGESTED", "DROP"),
        "congested_rally": _example(records, "CONGESTED", "RALLY"),
        "borderline": next(
            (item for item in records if item["structural_state"] == "BORDERLINE"),
            None,
        ),
        "sonacoms": sonacoms[0] if sonacoms else None,
    }
    review_set = []
    for category, item in examples.items():
        if item is None:
            continue
        review_set.append(
            {
                "category": category,
                "suggested_label": (
                    "CLEAR_CONGESTED"
                    if item["structural_state"] == "CONGESTED"
                    else (
                        "CLEAR_VALID"
                        if item["structural_state"] in {"CLEAN", "ACCEPTABLE"}
                        else "BORDERLINE"
                    )
                ),
                "human_review_status": "PENDING",
                "evidence": item,
            }
        )
    payload = {
        "audit_only": True,
        "production_gate_active": False,
        "datasets": datasets,
        "combined": {
            "canonical_zones": len(records),
            "dashboard_visible": sum(item["dashboard_visible"] for item in records),
            "one_candle_leg_ins": sum(
                item["leg_in_candle_count"] == 1 for item in records
            ),
            "multi_candle_leg_ins": sum(
                item["leg_in_candle_count"] > 1 for item in records
            ),
            "structural_states": dict(
                Counter(item["structural_state"] for item in records)
            ),
        },
        "threshold_study": {
            name: _impact(records, predicate) for name, predicate in RULES.items()
        },
        "examples": examples,
        "sonacoms": sonacoms,
    }
    TARGET.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    REVIEW_TARGET.write_text(json.dumps(review_set, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {key: payload[key] for key in ("combined", "threshold_study")}, indent=2
        )
    )
    print(f"WROTE {TARGET}")
    print(f"WROTE {REVIEW_TARGET}")


if __name__ == "__main__":
    main()
