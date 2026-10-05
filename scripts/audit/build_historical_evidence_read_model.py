#!/usr/bin/env python
# flake8: noqa: E402,E501
"""Package the verified frozen Milestone 9C shards into immutable SQLite."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.historical_evidence.constants import (
    DATASET_PERIOD,
    EXPECTED_RECORD_COUNT,
    EXPECTED_SHARD_SHA256,
    EXPECTED_TC_COUNTS,
    HISTORICAL_EVIDENCE_VERSION,
)

METHODOLOGY_MANIFEST = {
    "formation": "canonical-formation-1.1",
    "boundary": "canonical-boundary-frozen-milestone-9c",
    "lifecycle": "canonical-lifecycle-frozen-milestone-9c",
    "authenticity": "canonical-authenticity-frozen-milestone-9c",
    "zone_quality": "alphaedge-canonical-zone-quality-frozen-milestone-9c",
    "htf_location": "canonical-htf-location-frozen-milestone-9c",
    "trend": "canonical-trend-milestone-6",
    "trade_confidence": "canonical-trade-confidence-40-35-25-milestone-7f",
    "trade_planning": "canonical-trade-planning-1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _fingerprint() -> str:
    payload = {
        "historical_evidence_version": HISTORICAL_EVIDENCE_VERSION,
        "methodology": METHODOLOGY_MANIFEST,
        "sources": EXPECTED_SHARD_SHA256,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


SCHEMA = """
CREATE TABLE metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE historical_zones (
  zone_id TEXT PRIMARY KEY,
  symbol TEXT NOT NULL,
  timeframe TEXT NOT NULL CHECK(timeframe IN ('1D','1W')),
  pattern TEXT NOT NULL CHECK(pattern IN ('DBR','RBR','RBD','DBD')),
  zone_type TEXT NOT NULL CHECK(zone_type IN ('DEMAND','SUPPLY')),
  planning_timestamp TEXT NOT NULL,
  planning_year INTEGER NOT NULL,
  zone_low REAL NOT NULL,
  zone_high REAL NOT NULL,
  lifecycle_status TEXT NOT NULL,
  authenticity_status TEXT NOT NULL,
  interacted INTEGER NOT NULL CHECK(interacted IN (0,1)),
  interaction_timestamp TEXT,
  candles_to_interaction INTEGER,
  structural_failure INTEGER NOT NULL CHECK(structural_failure IN (0,1)),
  target_available INTEGER NOT NULL CHECK(target_available IN (0,1)),
  target_achieved INTEGER NOT NULL CHECK(target_achieved IN (0,1)),
  structural_target REAL,
  mfe_price REAL,
  mae_price REAL,
  mfe_zone_width REAL,
  mae_zone_width REAL,
  zone_quality_score REAL NOT NULL,
  zone_quality_label TEXT NOT NULL,
  trade_confidence_score REAL NOT NULL,
  trade_confidence_label TEXT NOT NULL,
  trade_confidence_sufficiency TEXT NOT NULL,
  trade_confidence_conflicted INTEGER NOT NULL CHECK(trade_confidence_conflicted IN (0,1)),
  htf_relationship TEXT,
  htf_compatibility TEXT,
  trend_alignment TEXT
) WITHOUT ROWID;

CREATE INDEX idx_he_primary_cohort ON historical_zones
  (timeframe, zone_type, pattern, zone_quality_label, trade_confidence_label, planning_year, symbol);
CREATE INDEX idx_he_tc ON historical_zones (trade_confidence_label, interacted, mfe_zone_width);
CREATE INDEX idx_he_zq ON historical_zones (zone_quality_label, interacted, mfe_zone_width);
CREATE INDEX idx_he_symbol_time ON historical_zones (symbol, planning_timestamp, zone_id);
CREATE INDEX idx_he_outcomes ON historical_zones (interacted, target_available, target_achieved, structural_failure);
CREATE INDEX idx_he_mfe ON historical_zones (interacted, mfe_zone_width);
CREATE INDEX idx_he_mae ON historical_zones (interacted, mae_zone_width);
CREATE INDEX idx_he_tc_cohort ON historical_zones
  (timeframe, zone_type, pattern, trade_confidence_label, interacted);
CREATE INDEX idx_he_zq_cohort ON historical_zones
  (timeframe, zone_type, pattern, zone_quality_label, interacted);
"""


def _record(
    snapshot: dict[str, Any], observation: dict[str, Any], context: dict[str, Any]
) -> tuple[Any, ...]:
    zq = context["zone_quality"]
    tc = context["trade_confidence"]
    interacted = observation.get("entry_index") is not None
    return (
        snapshot["zone_id"],
        snapshot["symbol"],
        snapshot["timeframe"],
        snapshot["pattern"],
        snapshot["zone_type"],
        snapshot["planning_timestamp"],
        int(snapshot["planning_timestamp"][:4]),
        snapshot["interaction_low"],
        snapshot["interaction_high"],
        snapshot["selected_lifecycle_status"],
        snapshot["selected_authenticity_status"],
        int(interacted),
        observation.get("entry_timestamp"),
        observation.get("candles_to_entry"),
        int(observation.get("first_structural_failure_index") is not None),
        int(interacted and observation.get("target_price") is not None),
        int(
            interacted
            and observation.get("target_price") is not None
            and observation.get("first_target_index") is not None
        ),
        observation.get("target_price"),
        observation.get("mfe_price"),
        observation.get("mae_price"),
        observation.get("mfe_zone_width"),
        observation.get("mae_zone_width"),
        zq["score"],
        zq["label"],
        tc["score"],
        tc["label"],
        tc["data_sufficiency"],
        int(tc["conflicted"]),
        tc.get("htf_relationship"),
        tc.get("htf_compatibility"),
        tc.get("trend_alignment"),
    )


INSERT = (
    "INSERT INTO historical_zones VALUES (" + ",".join("?" for _ in range(31)) + ")"
)


def build(source_dir: Path, output: Path) -> dict[str, Any]:
    actual_hashes: dict[str, str] = {}
    shards: list[dict[str, Any]] = []
    for name, expected in EXPECTED_SHARD_SHA256.items():
        path = source_dir / name
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"Frozen source checksum mismatch for {name}: {actual}")
        actual_hashes[name] = actual
        shard = json.loads(path.read_text(encoding="utf-8"))
        if not shard["audit"].get("complete"):
            raise RuntimeError(f"Frozen source shard is incomplete: {name}")
        shards.append(shard)

    records: list[tuple[Any, ...]] = []
    seen: set[str] = set()
    for shard in shards:
        for symbol in shard["symbols"].values():
            if symbol["status"] != "PROCESSED":
                continue
            observations = {row["zone_id"]: row for row in symbol["observations"]}
            contexts = {row["zone_id"]: row for row in symbol["contexts"]}
            for snapshot in symbol["snapshots"]:
                zone_id = snapshot["zone_id"]
                if (
                    zone_id in seen
                    or zone_id not in observations
                    or zone_id not in contexts
                ):
                    raise RuntimeError(
                        f"Duplicate or incomplete frozen record: {zone_id}"
                    )
                seen.add(zone_id)
                records.append(
                    _record(snapshot, observations[zone_id], contexts[zone_id])
                )

    if len(records) != EXPECTED_RECORD_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_RECORD_COUNT} records, found {len(records)}"
        )
    tc_counts = {label: 0 for label in EXPECTED_TC_COUNTS}
    for record in records:
        tc_counts[record[25]] += 1
    if tc_counts != EXPECTED_TC_COUNTS:
        raise RuntimeError(f"Trade Confidence reconciliation failed: {tc_counts}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        dir=output.parent, suffix=".sqlite3", delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        connection = sqlite3.connect(temporary_path)
        connection.executescript(SCHEMA)
        connection.executemany(INSERT, records)
        metadata = {
            "historical_evidence_version": HISTORICAL_EVIDENCE_VERSION,
            "methodology_fingerprint": _fingerprint(),
            "methodology": METHODOLOGY_MANIFEST,
            "dataset_period": DATASET_PERIOD,
            "record_count": EXPECTED_RECORD_COUNT,
            "trade_confidence_counts": EXPECTED_TC_COUNTS,
            "source_shard_sha256": actual_hashes,
            "source_universe": "nse500",
            "requested_symbols": 500,
            "processed_symbols": 499,
            "excluded_symbols": ["CHENNPETRO"],
            "supported_timeframes": ["1D", "1W"],
            "generated_from": "frozen-milestone-9c-shards",
        }
        connection.executemany(
            "INSERT INTO metadata(key,value) VALUES (?,?)",
            [
                (key, json.dumps(value, sort_keys=True))
                for key, value in metadata.items()
            ],
        )
        connection.execute(f"PRAGMA user_version = {901}")
        connection.commit()
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        connection.close()
        if integrity != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {integrity}")
        temporary_path.replace(output)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()
    result = {
        "output": str(output),
        "records": len(records),
        "tc_counts": tc_counts,
        "methodology_fingerprint": _fingerprint(),
        "artifact_sha256": sha256(output),
        "source_sha256": actual_hashes,
    }
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result["manifest"] = str(manifest_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", default="tmp/milestone9c")
    parser.add_argument(
        "--output",
        default=f"backend/historical_evidence/data/historical-evidence-{HISTORICAL_EVIDENCE_VERSION}.sqlite3",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            build(Path(args.source_dir), Path(args.output)), indent=2, sort_keys=True
        )
    )


if __name__ == "__main__":
    main()
