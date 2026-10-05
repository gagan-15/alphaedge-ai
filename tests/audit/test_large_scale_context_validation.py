# flake8: noqa: E501
"""Milestone 9C scale, determinism, clustering, and leakage locks."""

from __future__ import annotations

import copy

import pandas as pd

from backend.research.large_scale_context_performance import analyze_shards
from backend.research.large_scale_historical_replay import (
    LargeScaleHistoricalReplayEngine,
)
from tests.fixtures.canonical_formation_cases import FORMATION_CASES


def _future(count: int, start: pd.Timestamp, price: float = 120.0) -> pd.DataFrame:
    index = pd.date_range(start + pd.Timedelta(days=1), periods=count, freq="D")
    return pd.DataFrame(
        {
            "Open": [price] * count,
            "High": [price + 1] * count,
            "Low": [price - 1] * count,
            "Close": [price + 0.2] * count,
            "Volume": [10_000] * count,
        },
        index=index,
    )


def test_complete_context_is_future_candle_invariant() -> None:
    original = FORMATION_CASES["dbr_strong"].copy()
    original.index = pd.date_range("2024-01-01", periods=len(original), freq="D")
    original = pd.concat([original, _future(1, original.index[-1])])
    extended = pd.concat([original, _future(100, original.index[-1])])
    engine = LargeScaleHistoricalReplayEngine()

    before = engine.replay(
        original,
        symbol="TEST",
        timeframe="1D",
        location=original,
        trend=original,
    )
    after = LargeScaleHistoricalReplayEngine().replay(
        extended,
        symbol="TEST",
        timeframe="1D",
        location=extended,
        trend=extended,
    )

    zone_id = before["snapshots"][0]["zone_id"]
    before_context = next(row for row in before["contexts"] if row["zone_id"] == zone_id)
    after_context = next(row for row in after["contexts"] if row["zone_id"] == zone_id)
    assert before["snapshots"][0] == next(
        row for row in after["snapshots"] if row["zone_id"] == zone_id
    )
    assert before_context == after_context


def _record(zone_id: str, timestamp: str, *, label: str = "HIGH") -> tuple[dict, dict, dict]:
    snapshot = {
        "zone_id": zone_id,
        "symbol": "TEST",
        "timeframe": "1D",
        "pattern": "DBR",
        "zone_type": "DEMAND",
        "planning_timestamp": timestamp,
        "interaction_low": 100.0,
        "interaction_high": 105.0,
    }
    observation = {
        "zone_id": zone_id,
        "entry_policy": "PROXIMAL",
        "entry_index": 10,
        "first_structural_failure_index": None,
        "first_target_index": None,
        "target_price": None,
        "mfe_zone_width": 2.5,
        "mae_zone_width": 0.2,
    }
    context = {
        "zone_id": zone_id,
        "zone_quality": {"status": "AVAILABLE", "score": 80.0, "label": "STRONG"},
        "trade_confidence": {
            "status": "AVAILABLE",
            "score": 75.0,
            "label": label,
            "data_sufficiency": "FULL",
            "conflicted": False,
            "htf_relationship": "FULL_OVERLAP",
            "htf_compatibility": "ALIGNED",
            "trend_alignment": "ALIGNED",
            "zone_quality_contribution": 32.0,
            "htf_contribution": 25.0,
            "trend_contribution": 18.0,
        },
    }
    return snapshot, observation, context


def test_analysis_is_deterministic_and_reports_cluster_sensitivity() -> None:
    first = _record("z1", "2024-01-01T00:00:00")
    second = _record("z2", "2024-01-05T00:00:00")
    shard = {
        "symbols": {
            "TEST": {
                "status": "PROCESSED",
                "zero_range_candles": 0,
                "series": [{"first": "2024-01-01", "last": "2024-12-31"}],
                "snapshots": [first[0], second[0]],
                "observations": [first[1], second[1]],
                "contexts": [first[2], second[2]],
            }
        }
    }

    one = analyze_shards([copy.deepcopy(shard)])
    two = analyze_shards([copy.deepcopy(shard)])

    assert one == two
    assert one["table_q_cluster_sensitivity"]["raw"]["detected"] == 2
    assert one["table_q_cluster_sensitivity"]["cluster_independent"]["detected"] == 1
    assert one["dataset"]["total_canonical_zones"] == 2
