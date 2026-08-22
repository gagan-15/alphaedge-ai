"""Generate the frozen before/after report for canonical Formation V1.1."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.engines.demand_supply_engine.leg_in_structural_evidence_engine import (  # noqa: E402,E501
    LegInStructuralEvidenceEngine,
)
from backend.models.leg_in_structural_evidence import (  # noqa: E402
    LegInFormationValidity,
)

FIXTURE_DIR = Path("tests/fixtures/leg_in_structural")
TARGET = FIXTURE_DIR / "leg_in_formation_v1_1_report.json"
FILES = (
    "daily_nse500.json",
    "weekly_nifty100.json",
    "minute_15_nifty50.json",
    "minute_75_nifty50.json",
    "minute_125_nifty50.json",
)


def _decision(item):
    return LegInStructuralEvidenceEngine._formation_validity(
        width_ratio=item["displacement_zone_width_ratio"],
        efficiency=item["directional_efficiency"],
        pre_leg_in_occupancy=item.get("pre_leg_in_occupancy_ratio"),
        body_overlap=item.get("adjacent_body_overlap_ratio", 0.0),
        direction_changes=item["approach_direction_changes"],
        stop_reason=item["backward_walk_stop_reason"],
    )


def main() -> None:
    datasets = {}
    all_records = []
    for name in FILES:
        payload = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
        records = payload["records"]
        rejected = [
            item
            for item in records
            if _decision(item)[0] != LegInFormationValidity.VALID
        ]
        datasets[payload["timeframe"]] = {
            "canonical_before": len(records),
            "canonical_after": len(records) - len(rejected),
            "rejected": len(rejected),
            "rejection_percentage": round(
                100 * len(rejected) / max(len(records), 1), 3
            ),
            "dashboard_qualified_before": sum(
                item["dashboard_qualified"] for item in records
            ),
            "dashboard_qualified_after": sum(
                item["dashboard_qualified"] for item in records if item not in rejected
            ),
            "dashboard_visible_before": sum(
                item["dashboard_visible"] for item in records
            ),
            "dashboard_visible_after": sum(
                item["dashboard_visible"] for item in records if item not in rejected
            ),
        }
        all_records.extend(records)
    rejected = [
        item
        for item in all_records
        if _decision(item)[0] != LegInFormationValidity.VALID
    ]
    visible_removed = [item for item in rejected if item["dashboard_visible"]]
    survivors = [
        item
        for item in all_records
        if item not in rejected and item["dashboard_visible"]
    ]
    started = perf_counter()
    for _ in range(100):
        for item in all_records:
            _decision(item)
    elapsed = perf_counter() - started
    payload = {
        "rule": {
            "canonical_formation_version": "1.1",
            "max_weak_displacement_zone_width_ratio": 0.25,
            "max_extremely_poor_directional_efficiency": 0.10,
            "min_repeated_pre_leg_in_occupancy": 0.90,
            "min_meaningful_body_overlap": 0.50,
            "min_repeated_direction_changes": 2,
            "required_categories": [
                "weak directional approach",
                "prior occupancy",
                "one additional congestion confirmation",
            ],
            "extreme_pre_base_congestion": {
                "min_pre_leg_in_occupancy": 1.0,
                "min_adjacent_body_overlap": 1.0,
                "required_stop_reason": "SECOND_PAUSE_OR_CONGESTION",
                "min_direction_changes": 1,
                "max_directional_efficiency": 0.46,
                "max_displacement_zone_width_ratio": 0.50,
                "reason_code": "LEG_IN_EXTREME_PRE_BASE_CONGESTION",
            },
        },
        "datasets": datasets,
        "combined": {
            "before": len(all_records),
            "after": len(all_records) - len(rejected),
            "rejected": len(rejected),
            "rejection_percentage": round(100 * len(rejected) / len(all_records), 3),
            "dashboard_visible_before": sum(
                item["dashboard_visible"] for item in all_records
            ),
            "dashboard_visible_after": sum(
                item["dashboard_visible"]
                for item in all_records
                if item not in rejected
            ),
            "patterns_removed": dict(Counter(item["pattern"] for item in rejected)),
            "types_removed": dict(Counter(item["zone_type"] for item in rejected)),
            "one_candle_removed": sum(
                item["leg_in_candle_count"] == 1 for item in rejected
            ),
            "multi_candle_removed": sum(
                item["leg_in_candle_count"] > 1 for item in rejected
            ),
        },
        "removed_dashboard_zones": [
            {
                **item,
                "zone_quality_before": "Not stored in the frozen formation fixture",
                "v1_rejection_reasons": list(_decision(item)[1]),
            }
            for item in visible_removed
        ],
        "representative_survivors": survivors[:20],
        "performance": {
            "decision_calls": len(all_records) * 100,
            "total_seconds": round(elapsed, 6),
            "microseconds_per_decision": round(
                elapsed * 1_000_000 / (len(all_records) * 100), 3
            ),
        },
    }
    TARGET.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "datasets": datasets,
                "combined": payload["combined"],
                "performance": payload["performance"],
            },
            indent=2,
        )
    )
    print(f"WROTE {TARGET}")


if __name__ == "__main__":
    main()
