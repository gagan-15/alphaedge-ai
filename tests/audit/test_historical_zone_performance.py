from backend.research.historical_zone_performance import analyze_replay, wilson_rate
from scripts.audit.report_historical_zone_performance import merge_payloads


def _payload():
    snapshot = {
        "zone_id": "z1",
        "timeframe": "1D",
        "planning_timestamp": "2024-01-02",
        "selected_lifecycle_status": "FRESH",
        "selected_authenticity_status": "AUTHENTIC",
    }
    observation = {
        "zone_id": "z1",
        "symbol": "TEST",
        "timeframe": "1D",
        "pattern": "DBR",
        "zone_type": "DEMAND",
        "entry_policy": "PROXIMAL",
        "stop_policy": "A",
        "entry_index": 10,
        "first_structural_failure_index": None,
        "first_target_index": 12,
        "target_price": 110,
        "mfe_zone_width": 2.5,
        "mae_zone_width": 0.25,
        "mfe_atr": 1.2,
        "mae_atr": 0.1,
        "candles_to_entry": 3,
    }
    duplicate_stop = dict(observation, stop_policy="B")
    return {
        "dataset": {"series_requested": 1, "series_succeeded": 1, "series_failed": 0},
        "snapshots": [snapshot],
        "observations": [observation, duplicate_stop],
        "failures": [],
        "limitations": [],
    }


def test_one_zone_is_not_double_counted_across_stop_policies():
    result = analyze_replay(_payload())
    assert result["overall"]["detected"] == 1
    assert result["overall"]["reaction_rates"]["2"].numerator == 1


def test_missing_point_in_time_fields_are_excluded_not_reconstructed():
    result = analyze_replay(_payload())
    assert "zone_quality" in result["excluded_metrics"]
    assert "trade_confidence" in result["excluded_metrics"]


def test_wilson_interval_is_bounded_and_explicit():
    rate = wilson_rate(75, 100)
    assert rate.percent == 75.0
    assert 0 <= rate.ci_low < rate.percent < rate.ci_high <= 100
    assert wilson_rate(0, 0).percent is None


def test_future_observation_cannot_change_historical_grouping():
    payload = _payload()
    before = analyze_replay(payload)
    payload["observations"][0]["future_only_noise"] = 999
    after = analyze_replay(payload)
    assert before["by_year"] == after["by_year"]


def test_batch_merge_drops_noncanonical_cli_parse_failure():
    daily = _payload()
    daily["dataset"].update(symbols_requested=1, date_start="2024", date_end="2024")
    daily["failures"] = [{"symbol": "TEST", "timeframe": "1"}]
    weekly = _payload()
    weekly["snapshots"][0]["zone_id"] = "z2"
    weekly["snapshots"][0]["timeframe"] = "1W"
    weekly["observations"][0]["zone_id"] = "z2"
    weekly["observations"][0]["timeframe"] = "1W"
    weekly["observations"] = weekly["observations"][:1]
    weekly["dataset"].update(symbols_requested=1, date_start="2024", date_end="2024")
    merged = merge_payloads([daily, weekly])
    assert merged["dataset"]["series_failed"] == 0
    assert merged["dataset"]["series_requested"] == 2
