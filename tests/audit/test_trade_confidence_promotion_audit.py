import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "tests/fixtures/trade_confidence_same_zone_comparison.json"


def _report() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_frozen_audit_is_exact_same_zone_and_complete() -> None:
    report = _report()
    assert report["coverage"]["symbols_requested"] == 500
    assert report["coverage"]["symbols_processed"] == 500
    assert report["coverage"]["both"] == 55
    assert report["coverage"]["unmatched"] == 0
    identities = [item["zone_identity"] for item in report["records"]]
    assert len(identities) == len(set(identities)) == 55


def test_user_facing_legacy_score_path_is_explicit() -> None:
    report = _report()
    enrichment = report["legacy_enrichment"]
    assert enrichment["fully_enriched"] + enrichment["fallback_after_failure"] == 55
    assert all(item["legacy_score_path"] for item in report["records"])


def test_all_ranking_simulations_preserve_the_same_zone_population() -> None:
    report = _report()
    expected = {item["zone_identity"] for item in report["records"]}
    assert len(report["ranking_simulations"]) == 4
    for rows in report["ranking_simulations"].values():
        assert len(rows) == 20
        assert len({item["zone_identity"] for item in rows}) == 20
        assert {item["zone_identity"] for item in rows} <= expected


def test_contextual_candidate_never_places_conflicted_or_insufficient_first() -> None:
    report = _report()
    contextual = report["ranking_simulations"]["D_contextual_candidate"]
    assert all(
        item["context_bucket"] not in {"CONFLICTED", "INSUFFICIENT_CONTEXT"}
        for item in contextual
    )
