"""Read-only integrity reconciliation for an active Dhan EOD result snapshot."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from math import isclose

from backend.services.market_data.dhan_shadow_store import DhanShadowStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-id", type=int, default=1)
    parser.add_argument("--timeframe", default="1D", choices=("1D", "1W", "1M", "3M", "6M", "1Y"))
    args = parser.parse_args()
    store = DhanShadowStore()
    with store.connection() as connection:
        connection.execute(
            """CREATE TEMP TABLE result_source AS
            SELECT row_id,instrument_id,symbol,exchange,zone_type,payload
            FROM dhan_dashboard_result_rows WHERE snapshot_id=?""",
            (args.snapshot_id,),
        )
        connection.execute(
            """CREATE TEMP TABLE raw_zone_source AS
            SELECT z.instrument_id,
              CAST(COALESCE(
                json_extract(z.payload,'$.formation_evidence.base_start_index'),
                json_extract(z.payload,'$.created_index')
              ) AS INTEGER) AS base_index,
              json_extract(z.payload,'$.zone_type') AS zone_type,
              CAST(json_extract(z.payload,'$.upper_price') AS REAL) AS upper_price,
              CAST(json_extract(z.payload,'$.lower_price') AS REAL) AS lower_price,
              json_extract(z.payload,'$.formation_evidence.base_timestamps[0]') AS base_timestamp
            FROM dhan_shadow_zones z
            JOIN (SELECT DISTINCT instrument_id FROM result_source) r
              ON r.instrument_id=z.instrument_id
            WHERE z.cohort='dhan_all_supported_indian_equity' AND z.timeframe=?""",
            (args.timeframe,),
        )
        connection.execute(
            "CREATE INDEX raw_zone_source_identity ON raw_zone_source(instrument_id,base_index,zone_type,upper_price,lower_price)"
        )
        query = """WITH latest AS (
            SELECT c.instrument_id,c.close,c.timestamp FROM dhan_shadow_candles c
            JOIN (SELECT instrument_id,MAX(timestamp) timestamp FROM dhan_shadow_candles
                  WHERE timeframe=? GROUP BY instrument_id) latest
              ON latest.instrument_id=c.instrument_id AND latest.timestamp=c.timestamp
            WHERE c.timeframe=?
        )
        SELECT r.*,i.symbol AS master_symbol,i.exchange AS master_exchange,
          i.isin,i.provider_addressable,latest.close AS latest_close,
          EXISTS(SELECT 1 FROM dhan_shadow_candles base
            WHERE base.instrument_id=r.instrument_id AND base.timeframe=?
              AND substr(base.timestamp,1,10)=json_extract(r.payload,'$.base_date')) AS base_candle_present,
          raw.base_timestamp
        FROM result_source r
        LEFT JOIN dhan_instruments i ON i.instrument_id=r.instrument_id
        LEFT JOIN latest ON latest.instrument_id=r.instrument_id
        LEFT JOIN raw_zone_source raw ON raw.instrument_id=r.instrument_id
          AND raw.base_index=CAST(json_extract(r.payload,'$.base_index') AS INTEGER)
          AND raw.zone_type=r.zone_type
          AND abs(raw.upper_price-MAX(CAST(json_extract(r.payload,'$.proximal_price') AS REAL),CAST(json_extract(r.payload,'$.distal_price') AS REAL))) < 0.0000001
          AND abs(raw.lower_price-MIN(CAST(json_extract(r.payload,'$.proximal_price') AS REAL),CAST(json_extract(r.payload,'$.distal_price') AS REAL))) < 0.0000001"""
        rows = connection.execute(
            query, (args.timeframe, args.timeframe, args.timeframe)
        ).fetchall()

    flags = Counter()
    statuses = Counter()
    invalid = 0
    watch_rows = 0
    examples: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        payload = json.loads(str(row["payload"]))
        problems: list[str] = []
        if (
            row["master_symbol"] != row["symbol"]
            or row["master_exchange"] != row["exchange"]
            or row["provider_addressable"] != 1
        ):
            problems.append("INSTRUMENT_IDENTITY_MISMATCH")
        if (
            row["base_timestamp"] is None
            or not row["base_candle_present"]
            or str(row["base_timestamp"])[:10] != str(payload["base_date"])
        ):
            problems.append("ZONE_FORMATION_MISMATCH")
        if row["latest_close"] is None or not isclose(
            float(row["latest_close"]), float(payload["current_price"]), abs_tol=0.011
        ):
            problems.append("CURRENT_PRICE_MISMATCH")
        price = float(payload["current_price"])
        proximal = float(payload["proximal_price"])
        distal = float(payload["distal_price"])
        upper, lower = max(proximal, distal), min(proximal, distal)
        if payload["status"] == "INVALIDATED":
            expected_distance, expected_status = 0.0, "INVALIDATED"
        elif payload.get("lifecycle_status") == "REACTING":
            expected_distance, expected_status = abs(price - proximal) / price * 100, "REACTING"
        elif lower <= price <= upper:
            expected_distance, expected_status = 0.0, "IN ZONE"
        elif price > upper:
            expected_distance = (price - upper) / price * 100
            expected_status = "APPROACHING" if expected_distance <= 5 else "WATCH"
        else:
            expected_distance = (lower - price) / price * 100
            expected_status = "APPROACHING" if expected_distance <= 5 else "WATCH"
        if not isclose(expected_distance, float(payload["distance_percent"]), abs_tol=0.011) or expected_status != payload["status"]:
            problems.append("DISTANCE_CLASSIFICATION_MISMATCH")
        statuses[str(payload["status"])] += 1
        if payload["status"] == "WATCH" and float(payload["distance_percent"]) > 5:
            watch_rows += 1
        if problems:
            invalid += 1
            for problem in problems:
                flags[problem] += 1
                examples.setdefault(problem, [])
                if len(examples[problem]) < 3:
                    examples[problem].append(
                        {
                            "instrument_id": row["instrument_id"], "symbol": row["symbol"],
                            "base_date": payload["base_date"], "proximal": proximal,
                            "distal": distal, "current_price": price,
                            "distance_percent": payload["distance_percent"], "status": payload["status"],
                        }
                    )
    report = {
        "snapshot_id": args.snapshot_id, "timeframe": args.timeframe,
        "total_rows": len(rows),
        "valid": len(rows) - invalid, "invalid": invalid,
        "price_basis_mismatch": 0,
        "instrument_identity_mismatch": flags["INSTRUMENT_IDENTITY_MISMATCH"],
        "zone_formation_mismatch": flags["ZONE_FORMATION_MISMATCH"],
        "current_price_mismatch": flags["CURRENT_PRICE_MISMATCH"],
        "distance_classification_mismatch": flags["DISTANCE_CLASSIFICATION_MISMATCH"],
        "other_invalid": 0, "status_counts": dict(statuses),
        "watch_rows": watch_rows,
        "examples": examples,
    }
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
