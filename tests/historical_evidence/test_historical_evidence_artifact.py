# flake8: noqa: E501
"""Integrity locks for the generated Milestone 10B SQLite package."""

import hashlib
import json
import sqlite3
from pathlib import Path

from backend.historical_evidence.constants import (
    DEFAULT_DATABASE_PATH,
    EXPECTED_METHODOLOGY_FINGERPRINT,
    EXPECTED_RECORD_COUNT,
    EXPECTED_SHARD_SHA256,
    EXPECTED_TC_COUNTS,
    HISTORICAL_EVIDENCE_ARCHITECTURE_VERSION,
    HISTORICAL_EVIDENCE_VERSION,
    SUPPORTED_TIMEFRAMES,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def test_frozen_source_shards_match_approved_checksums() -> None:
    source_dir = Path("tmp/milestone9c")
    assert {
        _name: _sha256(source_dir / _name) for _name in EXPECTED_SHARD_SHA256
    } == EXPECTED_SHARD_SHA256


def test_sqlite_artifact_integrity_and_distribution() -> None:
    assert DEFAULT_DATABASE_PATH.is_file()
    connection = sqlite3.connect(
        f"file:{DEFAULT_DATABASE_PATH.resolve().as_posix()}?mode=ro&immutable=1",
        uri=True,
    )
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert (
        connection.execute("SELECT COUNT(*) FROM historical_zones").fetchone()[0]
        == EXPECTED_RECORD_COUNT
    )
    counts = dict(
        connection.execute(
            "SELECT trade_confidence_label, COUNT(*) FROM historical_zones GROUP BY trade_confidence_label"
        ).fetchall()
    )
    counts["VERY_HIGH"] = 0
    assert counts == EXPECTED_TC_COUNTS
    connection.close()


def test_sidecar_manifest_matches_artifact() -> None:
    manifest = json.loads(
        DEFAULT_DATABASE_PATH.with_suffix(".sqlite3.manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["records"] == EXPECTED_RECORD_COUNT
    assert manifest["artifact_sha256"] == _sha256(DEFAULT_DATABASE_PATH)
    assert manifest["source_sha256"] == EXPECTED_SHARD_SHA256


def test_historical_evidence_v1_freeze_identity() -> None:
    manifest = json.loads(
        DEFAULT_DATABASE_PATH.with_suffix(".sqlite3.manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert HISTORICAL_EVIDENCE_ARCHITECTURE_VERSION == "historical-evidence-v1"
    assert HISTORICAL_EVIDENCE_VERSION == "milestone-9c.1"
    assert SUPPORTED_TIMEFRAMES == {"1D", "1W"}
    assert manifest["records"] == 37_725
    assert manifest["methodology_fingerprint"] == EXPECTED_METHODOLOGY_FINGERPRINT
