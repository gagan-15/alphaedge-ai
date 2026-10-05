"""Freeze multi-timeframe Leg-In structural shadow evidence.

Audit-only command. It imports the production scanner pipeline but never changes
eligibility, ranking, scoring, or API output.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
from time import perf_counter
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.api.scanner import (  # noqa: E402
    _INTRADAY_SOURCE,
    _TIMEFRAME_LABELS,
    _dashboard_qualification,
    _timeframe_data,
    _universe_service,
    _zone_config,
    _zone_engine,
    _zone_lifecycle_ui,
    _zone_market_data,
)

OUTPUT_DIR = Path("tests/fixtures/leg_in_structural")


def _percentiles(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    ordered = sorted(values)

    def at(fraction: float) -> float:
        return round(ordered[round((len(ordered) - 1) * fraction)], 6)

    return {
        "min": at(0),
        "p10": at(0.10),
        "p25": at(0.25),
        "median": at(0.50),
        "p75": at(0.75),
        "p90": at(0.90),
        "max": at(1),
    }


def _source(timeframe: str) -> tuple[str, str]:
    return _INTRADAY_SOURCE.get(timeframe, (_zone_config.period, _zone_config.interval))


def _load(symbol: str, timeframe: str):
    period, interval = _source(timeframe)
    try:
        validated = _zone_market_data.get_stock_data_segments(
            symbol=symbol, period=period, interval=interval
        )
        frames = tuple(
            frame
            for segment in validated.segments
            if not (frame := _timeframe_data(segment, timeframe)).empty
        )
        return frames[-1] if frames else None
    except Exception as error:  # audit records provider failures verbatim
        return {"error": type(error).__name__}


def _zone_record(symbol: str, timeframe: str, data, zone) -> dict[str, Any]:
    formation = zone.formation_evidence
    assert formation is not None
    evidence = formation.leg_in_structural_evidence
    assert evidence is not None
    label = _TIMEFRAME_LABELS[timeframe]
    lifecycle = _zone_lifecycle_ui.evaluate(
        [zone],
        data,
        symbol=symbol,
        timeframe=label,
        current_price=float(data["Close"].iloc[-1]),
    )[zone.created_index]
    qualification = _dashboard_qualification.qualify(zone, label)
    candle_rows = []
    for index in range(
        evidence.broader_approach_start_index,
        evidence.broader_approach_end_index + 1,
    ):
        row = data.iloc[index]
        classification = _zone_engine._candle_classifier.classify(data, index)
        candle_rows.append(
            {
                "index": index,
                "timestamp": str(data.index[index]),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "structure": classification.structure.value,
                "direction": classification.direction.value,
            }
        )
    lower, upper = sorted((float(zone.lower_price), float(zone.upper_price)))
    width = max(upper - lower, 1e-9)
    leg_start = formation.leg_in_start_index
    full_touch = []
    material_zone_touch = []
    body_touch = []
    range_overlaps = []
    body_overlaps = []
    for position, candle in enumerate(candle_rows):
        candle_range = max(candle["high"] - candle["low"], 1e-9)
        overlap = max(0.0, min(candle["high"], upper) - max(candle["low"], lower))
        body_low = min(candle["open"], candle["close"])
        body_high = max(candle["open"], candle["close"])
        body_size = max(body_high - body_low, 1e-9)
        body_zone_overlap = max(0.0, min(body_high, upper) - max(body_low, lower))
        full_touch.append(overlap / candle_range >= 0.25)
        material_zone_touch.append(overlap / width >= 0.25)
        body_touch.append(body_zone_overlap / body_size >= 0.25)
        if position:
            previous = candle_rows[position - 1]
            previous_range = max(previous["high"] - previous["low"], 1e-9)
            adjacent_overlap = max(
                0.0,
                min(previous["high"], candle["high"])
                - max(previous["low"], candle["low"]),
            )
            range_overlaps.append(
                adjacent_overlap / max(min(previous_range, candle_range), 1e-9)
            )
            previous_body_low = min(previous["open"], previous["close"])
            previous_body_high = max(previous["open"], previous["close"])
            adjacent_body_overlap = max(
                0.0,
                min(previous_body_high, body_high) - max(previous_body_low, body_low),
            )
            body_overlaps.append(
                adjacent_body_overlap
                / max(min(previous_body_high - previous_body_low, body_size), 1e-9)
            )
    pre_count = max(0, leg_start - evidence.broader_approach_start_index)
    leg_count = len(candle_rows) - pre_count
    pre_occupancy = sum(full_touch[:pre_count]) / pre_count if pre_count else None
    weighted_denominator = pre_count + 0.25 * leg_count
    weighted_occupancy = (
        (sum(full_touch[:pre_count]) + 0.25 * sum(full_touch[pre_count:]))
        / weighted_denominator
        if weighted_denominator
        else 0.0
    )
    return {
        "symbol": symbol,
        "timeframe": label,
        "zone_id": lifecycle.zone_id,
        "pattern": formation.pattern,
        "zone_type": zone.zone_type.value,
        "proximal": (
            zone.upper_price if zone.zone_type.value == "DEMAND" else zone.lower_price
        ),
        "distal": (
            zone.lower_price if zone.zone_type.value == "DEMAND" else zone.upper_price
        ),
        "created_index": zone.created_index,
        "formation_timestamp": str(data.index[zone.created_index]),
        "dashboard_qualified": qualification.dashboard_qualified,
        "dashboard_visible": (
            qualification.dashboard_qualified and lifecycle.dashboard_lifecycle_eligible
        ),
        "leg_in_start_index": formation.leg_in_start_index,
        "leg_in_end_index": formation.leg_in_end_index,
        "leg_in_candle_count": evidence.leg_in_candle_count,
        "broader_approach_start_index": evidence.broader_approach_start_index,
        "broader_approach_end_index": evidence.broader_approach_end_index,
        "approach_candle_count": evidence.approach_candle_count,
        "pause_candle_count": evidence.pause_candle_count,
        "backward_walk_stop_reason": evidence.backward_walk_stop_reason,
        "directional_displacement": evidence.directional_displacement,
        "total_approach_travel": evidence.total_approach_travel,
        "directional_efficiency": evidence.directional_efficiency,
        "displacement_zone_width_ratio": (evidence.displacement_zone_width_ratio),
        "displacement_volatility_ratio": (evidence.displacement_volatility_ratio),
        "approach_overlap_ratio": evidence.approach_overlap_ratio,
        "prior_zone_occupancy_ratio": evidence.prior_zone_occupancy_ratio,
        "pre_leg_in_occupancy_ratio": pre_occupancy,
        "weighted_full_approach_occupancy_ratio": round(weighted_occupancy, 6),
        "material_zone_width_occupancy_ratio": round(
            sum(material_zone_touch) / max(len(material_zone_touch), 1), 6
        ),
        "body_occupancy_ratio": round(sum(body_touch) / max(len(body_touch), 1), 6),
        "adjacent_body_overlap_ratio": round(
            sum(body_overlaps) / max(len(body_overlaps), 1), 6
        ),
        "material_adjacent_range_overlap_ratio": round(
            sum(value >= 0.25 for value in range_overlaps)
            / max(len(range_overlaps), 1),
            6,
        ),
        "approach_direction_changes": evidence.approach_direction_changes,
        "structural_state": evidence.structural_state.value,
        "reason_codes": list(evidence.reason_codes),
        "broader_approach_candles": candle_rows,
        "canonical_leg_in_candles": [
            _formation_candle(item) for item in formation.leg_in_candles
        ],
        "canonical_base_candles": [
            _formation_candle(item) for item in formation.base_candles
        ],
        "canonical_leg_out_candles": [
            _formation_candle(item) for item in formation.leg_out_candles
        ],
    }


def _formation_candle(item) -> dict[str, Any]:
    classification = item.classification
    return {
        "index": item.index,
        "timestamp": item.timestamp,
        "structure": classification.structure.value,
        "direction": classification.direction.value,
        "body": classification.body,
        "range": classification.candle_range,
        "body_ratio": classification.body_ratio,
        "explosive": classification.explosive,
    }


def _rule_pass(record: dict[str, Any], rule: str) -> bool:
    width = record["displacement_zone_width_ratio"]
    volatility = record["displacement_volatility_ratio"]
    occupancy = record["prior_zone_occupancy_ratio"]
    overlap = record["approach_overlap_ratio"]
    efficiency = record["directional_efficiency"]
    if rule == "WIDTH_050":
        return width >= 0.50
    if rule == "WIDTH_100":
        return width >= 1.00
    if rule == "VOL_075":
        return volatility is not None and volatility >= 0.75
    if rule == "VOL_100":
        return volatility is not None and volatility >= 1.00
    if rule == "OCC_080":
        return occupancy <= 0.80
    if rule == "OCC_065":
        return occupancy <= 0.65
    if rule == "OVERLAP_080":
        return overlap <= 0.80
    if rule == "COMBINED_LENIENT":
        return width >= 0.50 and not (
            occupancy > 0.80 and overlap > 0.80 and efficiency < 0.65
        )
    if rule == "COMBINED_BALANCED":
        return width >= 0.50 and not (
            occupancy > 0.80 and (overlap > 0.70 or efficiency < 0.50)
        )
    if rule == "TIERED_MINIMUM":
        return record["structural_state"] not in {
            "CONGESTED",
            "INSUFFICIENT_EVIDENCE",
        }
    raise ValueError(rule)


def _impact(records: list[dict[str, Any]], rule: str) -> dict[str, Any]:
    retained = [item for item in records if _rule_pass(item, rule)]
    rejected = [item for item in records if not _rule_pass(item, rule)]

    def count(items, key, value):
        return sum(item[key] == value for item in items)

    return {
        "rule": rule,
        "retained": len(retained),
        "rejected": len(rejected),
        "dashboard_retained": sum(item["dashboard_visible"] for item in retained),
        "dashboard_rejected": sum(item["dashboard_visible"] for item in rejected),
        "one_candle_retained": sum(
            item["leg_in_candle_count"] == 1 for item in retained
        ),
        "one_candle_rejected": sum(
            item["leg_in_candle_count"] == 1 for item in rejected
        ),
        "multi_candle_retained": sum(
            item["leg_in_candle_count"] > 1 for item in retained
        ),
        "multi_candle_rejected": sum(
            item["leg_in_candle_count"] > 1 for item in rejected
        ),
        "patterns_retained": {
            pattern: count(retained, "pattern", pattern)
            for pattern in ("DBR", "RBR", "RBD", "DBD")
        },
        "patterns_rejected": {
            pattern: count(rejected, "pattern", pattern)
            for pattern in ("DBR", "RBR", "RBD", "DBD")
        },
        "types_retained": {
            kind: count(retained, "zone_type", kind) for kind in ("DEMAND", "SUPPLY")
        },
        "types_rejected": {
            kind: count(rejected, "zone_type", kind) for kind in ("DEMAND", "SUPPLY")
        },
    }


def run(timeframe: str, universe: str, limit: int | None) -> dict[str, Any]:
    symbols = _universe_service.get_symbols(universe, None)
    if limit:
        symbols = symbols[:limit]
    started = perf_counter()
    with ThreadPoolExecutor(max_workers=_zone_config.scan_concurrency) as executor:
        loaded = list(executor.map(lambda symbol: _load(symbol, timeframe), symbols))
    load_seconds = perf_counter() - started
    records = []
    failures = []
    detection_started = perf_counter()
    for symbol, data in zip(symbols, loaded, strict=True):
        if data is None or isinstance(data, dict):
            failures.append(
                {
                    "symbol": symbol,
                    "reason": "NO_DATA" if data is None else data["error"],
                }
            )
            continue
        for zone in _zone_engine.detect_zones(data):
            if zone.formation_evidence is not None:
                records.append(_zone_record(symbol, timeframe, data, zone))
    detection_seconds = perf_counter() - detection_started
    metric_names = (
        "directional_displacement",
        "displacement_zone_width_ratio",
        "displacement_volatility_ratio",
        "approach_overlap_ratio",
        "prior_zone_occupancy_ratio",
        "directional_efficiency",
        "approach_direction_changes",
        "approach_candle_count",
    )
    payload = {
        "audit_only": True,
        "production_gate_active": False,
        "timeframe": timeframe,
        "universe": universe,
        "symbols_requested": len(symbols),
        "symbols_processed": len(symbols) - len(failures),
        "failures": failures,
        "canonical_zones": len(records),
        "dashboard_qualified": sum(item["dashboard_qualified"] for item in records),
        "dashboard_visible": sum(item["dashboard_visible"] for item in records),
        "patterns": dict(Counter(item["pattern"] for item in records)),
        "zone_types": dict(Counter(item["zone_type"] for item in records)),
        "one_candle_leg_ins": sum(item["leg_in_candle_count"] == 1 for item in records),
        "multi_candle_leg_ins": sum(
            item["leg_in_candle_count"] > 1 for item in records
        ),
        "structural_states": dict(
            Counter(item["structural_state"] for item in records)
        ),
        "reason_codes": dict(
            Counter(code for item in records for code in item["reason_codes"])
        ),
        "metric_distributions": {
            name: _percentiles(
                [float(item[name]) for item in records if item[name] is not None]
            )
            for name in metric_names
        },
        "threshold_study": [
            _impact(records, rule)
            for rule in (
                "WIDTH_050",
                "WIDTH_100",
                "VOL_075",
                "VOL_100",
                "OCC_080",
                "OCC_065",
                "OVERLAP_080",
                "COMBINED_LENIENT",
                "COMBINED_BALANCED",
                "TIERED_MINIMUM",
            )
        ],
        "performance": {
            "data_load_seconds": round(load_seconds, 6),
            "detection_seconds": round(detection_seconds, 6),
            "detection_ms_per_zone": round(
                detection_seconds * 1000 / max(len(records), 1), 6
            ),
        },
        "records": records,
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--universe", default="nse500")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    payload = run(args.timeframe, args.universe, args.limit)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"_{args.limit}" if args.limit else ""
    target = OUTPUT_DIR / f"{args.timeframe.lower()}_{args.universe}{suffix}.json"
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {key: value for key, value in payload.items() if key != "records"},
            indent=2,
        )
    )
    print(f"WROTE {target}")


if __name__ == "__main__":
    main()
