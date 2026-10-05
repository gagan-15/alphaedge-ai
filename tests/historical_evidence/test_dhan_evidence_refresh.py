import sqlite3
import json

import pytest

from scripts.audit.refresh_dhan_historical_evidence import capture


def source(tmp_path):
    path = tmp_path / 'source.sqlite3'
    with sqlite3.connect(path) as connection:
        connection.executescript("""
        CREATE TABLE dhan_instruments(instrument_id, isin, exchange, symbol, provider_addressable);
        CREATE TABLE dhan_shadow_candles(instrument_id,timeframe,provider,timestamp,open,high,low,close,volume);
        INSERT INTO dhan_instruments VALUES ('NSE:1','TEST','NSE','TEST',1);
        INSERT INTO dhan_shadow_candles VALUES ('NSE:1','1D','dhan','2026-10-01T00:00:00+05:30',10,12,9,11,100);
        INSERT INTO dhan_shadow_candles VALUES ('NSE:1','1D','dhan','2026-10-03T00:00:00+05:30',11,13,10,12,100);
        """)
    return path


def test_capture_is_read_only_and_bounded(tmp_path):
    path = source(tmp_path)
    before = path.read_bytes()
    value = capture(path, tmp_path / 'inputs.json', '2021-08-18', '2026-10-01', ['TEST'])
    assert path.read_bytes() == before
    assert value['provider'] == 'dhan'
    assert len(value['symbols']['TEST']['candles']) == 1
    assert value['symbols']['TEST']['instrument_id'] == 'NSE:1'


def test_missing_identity_is_explicitly_excluded(tmp_path):
    path = source(tmp_path)
    result = capture(path, tmp_path / 'inputs.json', '2021-08-18', '2026-10-01', ['MISSING'])
    assert result['symbols']['MISSING']['exclusion_reason'] == 'DHAN_IDENTITY_UNAVAILABLE'
    assert result['symbols']['MISSING']['candles'] == []


def test_ambiguous_identity_is_not_guessed(tmp_path):
    path = source(tmp_path)
    with sqlite3.connect(path) as connection:
        connection.execute("INSERT INTO dhan_instruments VALUES ('NSE:2','TEST2','NSE','TEST',1)")
    result = capture(path, tmp_path / 'inputs.json', '2021-08-18', '2026-10-01', ['TEST'])
    assert result['symbols']['TEST']['exclusion_reason'] == 'DHAN_IDENTITY_AMBIGUOUS'
    assert result['symbols']['TEST']['instrument_id'] is None


def test_publisher_rejects_incomplete_run_without_touching_pointer(tmp_path):
    from scripts.audit.publish_dhan_historical_evidence import publish
    output = tmp_path / 'output'
    output.mkdir()
    pointer = output / 'current-dhan-evidence.json'
    pointer.write_text('previous')
    (tmp_path / 'status.json').write_text(json.dumps({'state':'REPLAY_INCOMPLETE','failed':1}))
    with pytest.raises(ValueError, match='Unresolved'):
        publish(tmp_path, output)
    assert pointer.read_text() == 'previous'


def test_latest_api_preserves_baseline_until_new_artifact(monkeypatch):
    from backend.api import historical_evidence as api
    from backend.historical_evidence import current
    from backend.historical_evidence.constants import HISTORICAL_EVIDENCE_VERSION
    monkeypatch.setattr(current, 'current_service', lambda: None)
    assert api.metadata('latest')['historical_evidence_version'] == HISTORICAL_EVIDENCE_VERSION
