"""Audit-only frozen legacy AI Score vs canonical Trade Confidence comparison."""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any


SOURCE = Path("tests/fixtures/trade_confidence_nse500_daily_snapshot.json")
TARGET = Path("tests/fixtures/trade_confidence_same_zone_comparison.json")
ENRICHED = Path("tests/fixtures/legacy_ai_score_enriched_snapshot.json")
ENRICHED_INPUTS = Path("tmp/trade7e/legacy-score-inputs.json")


def identity(item: dict[str, Any]) -> str:
    return ":".join(
        (
            item["symbol"].strip().upper(),
            item["timeframe"].strip().upper(),
            item["zone_type"].strip().upper(),
            (item.get("pattern_type") or "UNKNOWN").strip().upper(),
            f'{item["proximal_price"]:.8f}',
            f'{item["distal_price"]:.8f}',
            item["base_date"],
            str(item.get("zone_id") or item["base_index"]),
        )
    )


def legacy_fallback(item: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
    """Exact production fallback path: buildTradeConfidence(row, null, null)."""

    zone = "PASS" if item["zone_score"] >= 75 else "MIXED" if item["zone_score"] >= 60 else "FAIL"
    position = "PASS" if item["status"] == "IN ZONE" else "MIXED" if item["status"] == "APPROACHING" else "FAIL"
    confirmation = "MIXED" if item["status"] == "IN ZONE" or item["distance_percent"] <= 3 else "FAIL"
    factors = [
        ("zone", 20, zone), ("ema", 7, "UNAVAILABLE"),
        ("trend", 7, "UNAVAILABLE"), ("rsi", 5, "UNAVAILABLE"),
        ("volume", 5, "UNAVAILABLE"), ("timeframes", 10, "UNAVAILABLE"),
        ("sector", 7, "UNAVAILABLE"), ("relative", 7, "UNAVAILABLE"),
        ("breadth", 4, "UNAVAILABLE"), ("institutions", 4, "UNAVAILABLE"),
        ("sentiment", 4, "UNAVAILABLE"), ("risk", 8, "UNAVAILABLE"),
        ("confirmation", 6, confirmation), ("position", 6, position),
    ]
    score = round(sum(weight if status == "PASS" else weight * .5 if status == "MIXED" else 0 for _, weight, status in factors))
    return score, [{"key": key, "weight": weight, "status": status} for key, weight, status in factors]


def ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    output = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index
        while end + 1 < len(order) and values[order[end + 1]] == values[order[index]]:
            end += 1
        rank = (index + end + 2) / 2
        for position in range(index, end + 1):
            output[order[position]] = rank
        index = end + 1
    return output


def correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2 or pstdev(left) == 0 or pstdev(right) == 0:
        return None
    left_mean, right_mean = mean(left), mean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    denominator = math.sqrt(sum((a - left_mean) ** 2 for a in left) * sum((b - right_mean) ** 2 for b in right))
    return round(numerator / denominator, 6)


def stats(values: list[float]) -> dict[str, Any]:
    return {
        "minimum": min(values), "maximum": max(values),
        "mean": round(mean(values), 4), "median": round(median(values), 4),
        "standard_deviation": round(pstdev(values), 4),
        "distinct_scores": len(set(values)),
    }


def context_bucket(item: dict[str, Any]) -> tuple[int, str]:
    confidence = item["trade_confidence"]
    label = confidence["label"]
    sufficiency = confidence["data_sufficiency"]
    if label == "CONFLICTED":
        return 7, "CONFLICTED"
    if label == "INSUFFICIENT_CONTEXT" or sufficiency == "INSUFFICIENT":
        return 8, "INSUFFICIENT_CONTEXT"
    label_order = {"VERY_HIGH": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3}
    if sufficiency == "AVAILABLE":
        return label_order.get(label, 3), f"AVAILABLE_{label}"
    return 4 + label_order.get(label, 3), f"PARTIAL_{label}"


def ranking_rows(records: list[dict[str, Any]], key: Any) -> list[dict[str, Any]]:
    rows = sorted(records, key=key)
    return [
        {
            "rank": rank,
            "zone_identity": item["zone_identity"],
            "symbol": item["symbol"],
            "legacy_ai_score": item["legacy_ai_score"],
            "trade_confidence": item["trade_confidence"]["score"],
            "trade_confidence_label": item["trade_confidence"]["label"],
            "data_sufficiency": item["trade_confidence"]["data_sufficiency"],
            "context_bucket": context_bucket(item)[1],
            "zone_quality": item["zone_quality"],
            "distance_percent": item["distance_percent"],
        }
        for rank, item in enumerate(rows, 1)
    ]


def main() -> None:
    snapshot = json.loads(SOURCE.read_text(encoding="utf-8"))
    enriched_source = ENRICHED if ENRICHED.exists() else ENRICHED_INPUTS
    enriched = json.loads(enriched_source.read_text(encoding="utf-8"))
    enriched_by_id = {
        record["zone_identity"]: record for record in enriched.get("records", [])
    }
    records = []
    for item in snapshot["results"]:
        confidence = item.get("trade_confidence")
        if not confidence:
            continue
        zone_identity = identity(item)
        enriched_record = enriched_by_id.get(zone_identity)
        if enriched_record:
            legacy = enriched_record["legacy_ai_score"]
            factors = enriched_record["legacy_result"]["factors"]
            score_path = "FULLY_ENRICHED"
        else:
            legacy, factors = legacy_fallback(item)
            score_path = "PRODUCTION_FALLBACK_AFTER_ENRICHMENT_FAILURE"
        records.append(
            {
                "zone_identity": zone_identity,
                "symbol": item["symbol"], "timeframe": item["timeframe"],
                "zone_type": item["zone_type"], "pattern": item.get("pattern_type"),
                "proximal": item["proximal_price"], "distal": item["distal_price"],
                "formation_date": item["base_date"], "zone_id": item.get("zone_id"),
                "zone_quality": item["zone_score"], "zone_quality_label": item.get("zone_quality_label"),
                "lifecycle_state": item.get("lifecycle_status"),
                "legacy_ai_score": legacy, "legacy_components": factors,
                "legacy_score_path": score_path,
                "trade_confidence": confidence,
                "absolute_difference": round(abs(legacy - confidence["score"]), 2),
                "distance_percent": item["distance_percent"],
            }
        )
    legacy_values = [item["legacy_ai_score"] for item in records]
    confidence_values = [item["trade_confidence"]["score"] for item in records]
    differences = [item["absolute_difference"] for item in records]
    report = {
        "audit_kind": "PRE_MILESTONE_7E_AUDIT_ONLY",
        "snapshot_timestamp": snapshot["last_completed_at"],
        "coverage": {
            "symbols_requested": snapshot["total_symbols"],
            "symbols_processed": snapshot["processed_symbols"],
            "failures": snapshot["failed_symbols"],
            "canonical_zones": snapshot["canonical_zone_count"],
            "dashboard_qualified_zones": snapshot["total_zones"],
            "legacy_fallback_scores": len(records),
            "trade_confidence_scores": sum(bool(item.get("trade_confidence")) for item in snapshot["results"]),
            "both": len(records), "unmatched": snapshot["total_zones"] - len(records),
        },
        "legacy_ai_score_scope": "Exact user-facing production result: enriched where both requests succeeded, otherwise exact production fallback",
        "legacy_enrichment": {
            "fully_enriched": sum(item["legacy_score_path"] == "FULLY_ENRICHED" for item in records),
            "fallback_after_failure": sum(item["legacy_score_path"] != "FULLY_ENRICHED" for item in records),
            "failure_categories": {
                reason: sum(item["reason"] == reason for item in enriched.get("failures", []))
                for reason in sorted({item["reason"] for item in enriched.get("failures", [])})
            },
        },
        "legacy_ai_score": stats(legacy_values),
        "trade_confidence": stats(confidence_values),
        "pearson": correlation(legacy_values, confidence_values),
        "spearman": correlation(ranks(legacy_values), ranks(confidence_values)),
        "difference": {
            "mean_absolute": round(mean(differences), 4),
            "median_absolute": round(median(differences), 4),
            "maximum_absolute": max(differences),
        },
        "trade_confidence_labels": {label: sum(item["trade_confidence"]["label"] == label for item in records) for label in ("VERY_HIGH", "HIGH", "MODERATE", "LOW", "CONFLICTED", "INSUFFICIENT_CONTEXT")},
        "data_sufficiency": {state: sum(item["trade_confidence"]["data_sufficiency"] == state for item in records) for state in ("AVAILABLE", "PARTIAL", "INSUFFICIENT")},
        "top_disagreements": sorted(records, key=lambda item: (-item["absolute_difference"], item["zone_identity"]))[:20],
        "records": records,
    }
    report["ranking_simulations"] = {
        "A_current_production": ranking_rows(records, lambda item: (item["distance_percent"], -item["zone_quality"], item["zone_identity"]))[:20],
        "B_legacy_ai_score": ranking_rows(records, lambda item: (-item["legacy_ai_score"], item["distance_percent"], item["zone_identity"]))[:20],
        "C_trade_confidence_raw": ranking_rows(records, lambda item: (-item["trade_confidence"]["score"], item["distance_percent"], item["zone_identity"]))[:20],
        "D_contextual_candidate": ranking_rows(records, lambda item: (context_bucket(item)[0], -item["trade_confidence"]["score"], -item["zone_quality"], item["distance_percent"], item["zone_identity"]))[:20],
    }
    TARGET.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("coverage", "legacy_ai_score", "trade_confidence", "pearson", "spearman", "difference", "trade_confidence_labels", "data_sufficiency")}, indent=2))


if __name__ == "__main__":
    main()
