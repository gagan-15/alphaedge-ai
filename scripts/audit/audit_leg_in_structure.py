"""Shadow-only canonical Leg-In structural audit; never imported by production."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from statistics import median
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.api.scanner import (  # noqa: E402
    _dashboard_qualification,
    _timeframe_data,
    _universe_service,
    _zone_config,
    _zone_engine,
    _zone_lifecycle_ui,
    _zone_market_data,
)
from backend.engines.zone_scoring_engine.zone_scoring_engine import (  # noqa: E402
    ZoneScoringEngine,
)
from backend.models.departure import DepartureDirection  # noqa: E402
from backend.models.zone_scoring.canonical_zone_quality import (  # noqa: E402
    ZoneQualityContext,
)


TARGET = Path("tests/fixtures/canonical_leg_in_structural_audit.json")


def _overlap_ratio(low_a: float, high_a: float, low_b: float, high_b: float) -> float:
    overlap = max(0.0, min(high_a, high_b) - max(low_a, low_b))
    return overlap / max(min(high_a - low_a, high_b - low_b), 1e-9)


def _metrics(data, zone) -> dict[str, Any]:
    evidence = zone.formation_evidence
    assert evidence is not None
    start, end = evidence.leg_in_start_index, evidence.leg_in_end_index
    leg = data.iloc[start : end + 1]
    bearish = evidence.leg_in_direction == DepartureDirection.BEARISH
    net = (
        float(leg.iloc[0]["Open"]) - float(leg.iloc[-1]["Close"])
        if bearish
        else float(leg.iloc[-1]["Close"]) - float(leg.iloc[0]["Open"])
    )
    net = max(0.0, net)
    points = [float(leg.iloc[0]["Open"]), *map(float, leg["Close"])]
    travel = sum(abs(right - left) for left, right in zip(points, points[1:]))
    width = max(zone.upper_price - zone.lower_price, 1e-9)
    prior = data.iloc[max(0, start - 20) : start]
    ranges = [float(row.High - row.Low) for row in prior.itertuples() if row.High > row.Low]
    volatility = median(ranges) if ranges else None
    approach_start = max(0, start - 4)
    approach = data.iloc[approach_start : end + 1]
    overlaps = [
        _overlap_ratio(
            float(approach.iloc[index - 1]["Low"]),
            float(approach.iloc[index - 1]["High"]),
            float(approach.iloc[index]["Low"]),
            float(approach.iloc[index]["High"]),
        )
        for index in range(1, len(approach))
    ]
    occupancy = []
    for row in approach.itertuples():
        candle_range = max(float(row.High - row.Low), 1e-9)
        occupied = max(
            0.0,
            min(float(row.High), zone.upper_price)
            - max(float(row.Low), zone.lower_price),
        )
        occupancy.append(occupied / candle_range)
    candles = []
    relevant_start = max(0, start - 5)
    relevant_end = min(len(data) - 1, evidence.leg_out_end_index)
    classifications = {
        item.index: item.classification
        for item in (
            *evidence.leg_in_candles,
            *evidence.base_candles,
            *evidence.leg_out_candles,
        )
    }
    for index in range(relevant_start, relevant_end + 1):
        row = data.iloc[index]
        classification = classifications.get(index) or _zone_engine._candle_classifier.classify(data, index)
        role = "PRE_APPROACH"
        if start <= index <= end:
            role = "LEG_IN"
        elif evidence.base_start_index <= index <= evidence.base_end_index:
            role = "BASE"
        elif evidence.leg_out_start_index <= index <= evidence.leg_out_end_index:
            role = "LEG_OUT"
        overlap = max(
            0.0,
            min(float(row["High"]), zone.upper_price)
            - max(float(row["Low"]), zone.lower_price),
        )
        candles.append(
            {
                "index": index,
                "timestamp": str(data.index[index]),
                "role": role,
                "open": float(row["Open"]), "high": float(row["High"]),
                "low": float(row["Low"]), "close": float(row["Close"]),
                "range": classification.candle_range,
                "body": classification.body,
                "body_ratio": classification.body_ratio,
                "structure": classification.structure.value,
                "direction": classification.direction.value,
                "zone_overlap_fraction_of_candle": round(
                    overlap / max(classification.candle_range, 1e-9), 6
                ),
            }
        )
    efficiency = net / max(travel, 1e-9)
    overlap = sum(overlaps) / len(overlaps) if overlaps else 0.0
    occupancy_ratio = sum(value >= 0.25 for value in occupancy) / max(len(occupancy), 1)
    return {
        "leg_in_candle_count": len(leg),
        "directional_displacement": round(net, 6),
        "total_travel": round(travel, 6),
        "directional_efficiency": round(efficiency, 6),
        "displacement_zone_width_ratio": round(net / width, 6),
        "displacement_volatility_ratio": (
            round(net / volatility, 6) if volatility else None
        ),
        "approach_overlap_ratio": round(overlap, 6),
        "prior_zone_occupancy_ratio": round(occupancy_ratio, 6),
        "approach_window_start_index": approach_start,
        "approach_window_candles": len(approach),
        "diagnostic_congested": bool(
            efficiency < 0.5 and (overlap >= 0.55 or occupancy_ratio >= 0.4)
        ),
        "candles": candles,
    }


def _percentiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    def pick(fraction: float) -> float:
        return round(ordered[round((len(ordered) - 1) * fraction)], 4)
    return {"min": pick(0), "p10": pick(.1), "p25": pick(.25), "median": pick(.5), "p75": pick(.75), "p90": pick(.9), "max": pick(1)}


def main() -> None:
    symbols = _universe_service.get_symbols("nse500", None)
    def load(symbol: str):
        try:
            validated = _zone_market_data.get_stock_data_segments(
                symbol=symbol, period=_zone_config.period, interval=_zone_config.interval
            )
            segments = tuple(
                frame for segment in validated.segments
                if not (frame := _timeframe_data(segment, "DAILY")).empty
            )
            return segments[-1] if segments else None
        except Exception as error:
            return {"error": type(error).__name__}
    with ThreadPoolExecutor(max_workers=_zone_config.scan_concurrency) as executor:
        loaded = list(executor.map(load, symbols))
    records = []
    failures = []
    scorer = ZoneScoringEngine()
    for symbol, data in zip(symbols, loaded, strict=True):
        if data is None or isinstance(data, dict):
            failures.append({"symbol": symbol, "reason": "NO_DATA" if data is None else data["error"]})
            continue
        zones = _zone_engine.detect_zones(data)
        if not zones:
            continue
        qualifications = {zone.created_index: _dashboard_qualification.qualify(zone, "1D") for zone in zones}
        metadata = _zone_lifecycle_ui.evaluate(zones, data, symbol=symbol, timeframe="1D", current_price=float(data["Close"].iloc[-1]))
        contexts = {
            index: ZoneQualityContext(
                lifecycle_status=item.lifecycle_status,
                is_fresh=item.is_fresh,
                penetration_percent=item.current_penetration_percent,
                max_penetration_percent=item.max_penetration_percent,
                authenticity_status=item.authenticity_status,
            ) for index, item in metadata.items()
        }
        scores = {item.zone.created_index: item for item in scorer.score(zones, contexts).scored_zones}
        for zone in zones:
            evidence = zone.formation_evidence
            if evidence is None:
                continue
            qualification = qualifications[zone.created_index]
            lifecycle = metadata[zone.created_index]
            metric = _metrics(data, zone)
            records.append({
                "symbol": symbol, "timeframe": "1D", "pattern": evidence.pattern,
                "zone_type": zone.zone_type.value,
                "proximal": zone.upper_price if zone.zone_type.value == "DEMAND" else zone.lower_price,
                "distal": zone.lower_price if zone.zone_type.value == "DEMAND" else zone.upper_price,
                "formation_timestamp": str(data.index[zone.created_index]),
                "zone_id": lifecycle.zone_id,
                "dashboard_formation_qualified": qualification.dashboard_qualified,
                "dashboard_visible": qualification.dashboard_qualified and lifecycle.dashboard_lifecycle_eligible,
                "lifecycle": lifecycle.lifecycle_status,
                "zone_quality": scores[zone.created_index].total_score,
                "zone_quality_label": scores[zone.created_index].label,
                "departure_strength": evidence.departure_strength.value,
                **metric,
            })
    numeric = [
        "leg_in_candle_count", "directional_displacement", "total_travel",
        "directional_efficiency", "displacement_zone_width_ratio",
        "displacement_volatility_ratio", "approach_overlap_ratio",
        "prior_zone_occupancy_ratio",
    ]
    distributions = {
        key: _percentiles([float(item[key]) for item in records if item[key] is not None])
        for key in numeric
    }
    sensitivities = []
    for width_min in (0.5, 1.0, 1.5, 2.0):
        for efficiency_min in (0.35, 0.5, 0.65):
            passed = [item for item in records if item["displacement_zone_width_ratio"] >= width_min and item["directional_efficiency"] >= efficiency_min]
            sensitivities.append({
                "zone_width_min": width_min, "efficiency_min": efficiency_min,
                "retained": len(passed), "rejected": len(records) - len(passed),
                "dashboard_retained": sum(item["dashboard_visible"] for item in passed),
                "pattern_retained": {pattern: sum(item["pattern"] == pattern for item in passed) for pattern in ("DBR", "RBR", "RBD", "DBD")},
                "one_candle_retained": sum(item["leg_in_candle_count"] == 1 for item in passed),
                "multi_candle_retained": sum(item["leg_in_candle_count"] > 1 for item in passed),
            })
    suspicious = sorted(
        [item for item in records if item["diagnostic_congested"] or item["displacement_zone_width_ratio"] < 1],
        key=lambda item: (not item["dashboard_visible"], item["directional_efficiency"], item["displacement_zone_width_ratio"]),
    )
    sonacoms = [item for item in records if item["symbol"] == "SONACOMS" and abs(item["proximal"] - 720.5) < .01 and abs(item["distal"] - 707) < .01]
    payload = {
        "audit_only": True, "production_changed": False,
        "symbols_requested": len(symbols), "symbols_processed": len(symbols) - len(failures),
        "failures": failures, "canonical_zones": len(records),
        "dashboard_visible": sum(item["dashboard_visible"] for item in records),
        "patterns": {pattern: sum(item["pattern"] == pattern for item in records) for pattern in ("DBR", "RBR", "RBD", "DBD")},
        "zone_types": {kind: sum(item["zone_type"] == kind for item in records) for kind in ("DEMAND", "SUPPLY")},
        "one_candle_leg_ins": sum(item["leg_in_candle_count"] == 1 for item in records),
        "multi_candle_leg_ins": sum(item["leg_in_candle_count"] > 1 for item in records),
        "suspicious_count": len(suspicious),
        "suspicious_dashboard_count": sum(item["dashboard_visible"] for item in suspicious),
        "distributions": distributions, "sensitivity": sensitivities,
        "sonacoms": sonacoms, "suspicious_examples": suspicious[:40],
        "records": records,
    }
    TARGET.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("symbols_requested", "symbols_processed", "canonical_zones", "dashboard_visible", "patterns", "zone_types", "one_candle_leg_ins", "multi_candle_leg_ins", "suspicious_count", "suspicious_dashboard_count")}, indent=2))


if __name__ == "__main__":
    main()
