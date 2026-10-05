"""Build a deterministic stratified packet for independent human review."""

from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path

FIXTURE_DIR = Path("tests/fixtures/leg_in_structural")
JSON_TARGET = FIXTURE_DIR / "labelled_review_packet.json"
CSV_TARGET = FIXTURE_DIR / "labelled_review_packet.csv"
DATASETS = (
    ("daily_nse500.json", 70),
    ("weekly_nifty100.json", 21),
    ("minute_15_nifty50.json", 70),
    ("minute_75_nifty50.json", 45),
    ("minute_125_nifty50.json", 44),
)


def _ordered(records):
    return sorted(
        records,
        key=lambda item: (
            item["structural_state"],
            item["pattern"],
            item["zone_type"],
            item["leg_in_candle_count"] == 1,
            item["symbol"],
            item["formation_timestamp"],
        ),
    )


def _stratified(records, limit):
    buckets = {}
    for item in _ordered(records):
        key = (
            item["structural_state"],
            item["pattern"],
            "ONE" if item["leg_in_candle_count"] == 1 else "MULTI",
        )
        buckets.setdefault(key, []).append(item)
    selected = []
    keys = sorted(buckets)
    while len(selected) < limit:
        progressed = False
        for key in keys:
            if buckets[key] and len(selected) < limit:
                selected.append(buckets[key].pop(0))
                progressed = True
        if not progressed:
            break
    return selected


def _review_item(item):
    return {
        "review_id": f"LEG-IN-{item['zone_id']}-{item['timeframe']}",
        "human_review_label": "PENDING_HUMAN_REVIEW",
        "allowed_labels": [
            "CLEAR_VALID",
            "CLEAR_CONGESTED",
            "BORDERLINE",
            "INSUFFICIENT_EVIDENCE",
        ],
        "reviewer_notes": "",
        "chart_reference": {
            "symbol": item["symbol"],
            "timeframe": item["timeframe"],
            "formation_timestamp": item["formation_timestamp"],
            "approach_start_index": item["broader_approach_start_index"],
            "leg_out_end_index": item["canonical_leg_out_candles"][-1]["index"],
        },
        "evidence": item,
    }


def main() -> None:
    selected = []
    all_records = []
    for name, limit in DATASETS:
        payload = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
        all_records.extend(payload["records"])
        selected.extend(_stratified(payload["records"], limit))

    required = []
    for item in all_records:
        if (
            item["symbol"] == "SONACOMS"
            and item["pattern"] == "DBR"
            and abs(item["proximal"] - 720.5) < 0.02
            and abs(item["distal"] - 707.0) < 0.02
        ) or (
            item["symbol"] == "BLS"
            and item["pattern"] == "DBR"
            and abs(item["proximal"] - 239.8) < 0.02
            and abs(item["distal"] - 236.0) < 0.02
        ):
            required.append(item)
    selected_ids = {item["zone_id"] for item in selected}
    replacement_index = len(selected) - 1
    for item in required:
        if item["zone_id"] not in selected_ids:
            selected[replacement_index] = item
            selected_ids.add(item["zone_id"])
            replacement_index -= 1

    packet = [_review_item(item) for item in selected]
    summary = {
        "review_count": len(packet),
        "label_distribution": {"PENDING_HUMAN_REVIEW": len(packet)},
        "timeframes": dict(Counter(item["evidence"]["timeframe"] for item in packet)),
        "patterns": dict(Counter(item["evidence"]["pattern"] for item in packet)),
        "zone_types": dict(Counter(item["evidence"]["zone_type"] for item in packet)),
        "states": dict(
            Counter(item["evidence"]["structural_state"] for item in packet)
        ),
        "leg_in_sizes": dict(
            Counter(
                "ONE" if item["evidence"]["leg_in_candle_count"] == 1 else "MULTI"
                for item in packet
            )
        ),
        "required_cases": [item["symbol"] for item in required],
    }
    JSON_TARGET.write_text(
        json.dumps({"summary": summary, "reviews": packet}, indent=2),
        encoding="utf-8",
    )
    with CSV_TARGET.open("w", newline="", encoding="utf-8-sig") as stream:
        fields = (
            "review_id",
            "human_review_label",
            "symbol",
            "timeframe",
            "pattern",
            "zone_type",
            "proximal",
            "distal",
            "formation_timestamp",
            "leg_in_candle_count",
            "structural_state",
            "backward_walk_stop_reason",
            "displacement_zone_width_ratio",
            "displacement_volatility_ratio",
            "pre_leg_in_occupancy_ratio",
            "prior_zone_occupancy_ratio",
            "weighted_full_approach_occupancy_ratio",
            "material_zone_width_occupancy_ratio",
            "approach_overlap_ratio",
            "adjacent_body_overlap_ratio",
            "directional_efficiency",
            "reviewer_notes",
        )
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for item in packet:
            evidence = item["evidence"]
            writer.writerow(
                {
                    "review_id": item["review_id"],
                    "human_review_label": item["human_review_label"],
                    "reviewer_notes": item["reviewer_notes"],
                    **{field: evidence.get(field) for field in fields},
                }
            )
    print(json.dumps(summary, indent=2))
    print(f"WROTE {JSON_TARGET}")
    print(f"WROTE {CSV_TARGET}")


if __name__ == "__main__":
    main()
