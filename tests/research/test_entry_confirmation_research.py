"""Point-in-time regression tests for Milestone 11A research tooling."""

import pandas as pd

from backend.research.entry_confirmation_research import (
    EntryConfirmationResearchEngine,
    summarize_confirmation_observations,
)


def test_candidate_features_never_precede_interaction() -> None:
    records = [
        {
            "interaction_index": 10,
            "mfe_zone_width_from_interaction": 2.5,
            "structural_failure_index": None,
            "wick_rejection_index": 10,
            "close_recovery_index": 11,
            "engulfing_response_index": None,
            "displacement_index": 12,
            "failed_continuation_index": 11,
            "micro_structure_index": 13,
            "volume_expansion_index": None,
            "gap_response_index": None,
        }
    ]
    result = summarize_confirmation_observations(records)
    assert result["features"]["wick_rejection"]["median_delay_candles"] == 0
    assert result["features"]["micro_structure"]["median_delay_candles"] == 3


def test_feature_summary_keeps_coverage_loss_explicit() -> None:
    base = {
        "interaction_index": 4,
        "structural_failure_index": None,
        "wick_rejection_index": None,
        "close_recovery_index": None,
        "engulfing_response_index": None,
        "displacement_index": None,
        "failed_continuation_index": None,
        "micro_structure_index": None,
        "volume_expansion_index": None,
        "gap_response_index": None,
    }
    records = [
        {**base, "mfe_zone_width_from_interaction": 3.0, "close_recovery_index": 5},
        {**base, "mfe_zone_width_from_interaction": 0.5},
    ]
    result = summarize_confirmation_observations(records)
    assert result["baseline"]["observations"] == 2
    assert result["features"]["close_recovery"]["observations"] == 1
    assert result["features"]["close_recovery"]["coverage_percent"] == 50.0


def test_micro_structure_uses_only_preinteraction_level_and_current_closes() -> None:
    frame = pd.DataFrame(
        {
            "Open": [10, 11, 12, 11, 12],
            "High": [11, 12, 13, 12, 15],
            "Low": [9, 10, 11, 10, 11],
            "Close": [10.5, 11.5, 12.5, 11.5, 14],
            "Volume": [100] * 5,
        }
    )
    assert EntryConfirmationResearchEngine._micro_structure(frame, 3, 5, True) == 4
