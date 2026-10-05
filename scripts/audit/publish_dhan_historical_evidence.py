"""Validate and atomically select a complete, separate Dhan evidence artifact."""
import hashlib
import json
import sqlite3
from collections import Counter
from contextlib import closing
from pathlib import Path
from tempfile import NamedTemporaryFile

from backend.historical_evidence.constants import PACKAGE_ROOT, TC_LABELS
from scripts.audit.build_historical_evidence_read_model import SCHEMA, INSERT, _record, METHODOLOGY_MANIFEST, sha256


def publish(directory: Path, destination: Path | None = None):
    destination = destination or PACKAGE_ROOT / 'data'
    status = json.loads((directory / 'status.json').read_text())
    if status['state'] != 'REPLAY_COMPLETE' or status['failed']:
        raise ValueError('Unresolved evidence replay failures')
    source_path = directory / 'dhan-inputs.json'
    digest = sha256(source_path)
    if digest != status['source_sha256']:
        raise ValueError('Source hash mismatch')
    source = json.loads(source_path.read_text())
    if len(source['symbols']) != status['target']:
        raise ValueError('Cohort accounting mismatch')
    rows, exclusions, coverage = [], [], []
    for index, (symbol, item) in enumerate(source['symbols'].items(), 1):
        result = json.loads((directory / f'replay-{index:04d}.json').read_text())
        if result['symbol'] != symbol or result['source_sha256'] != digest or result['instrument_id'] != item['instrument_id']:
            raise ValueError('Checkpoint provenance mismatch')
        if result['status'] == 'EXCLUDED':
            if item['candles']:
                raise ValueError('Unexpected exclusion of available history')
            exclusions.append({'symbol': symbol, 'reason': result['reason']})
            continue
        if result['status'] != 'PROCESSED':
            raise ValueError('Unresolved checkpoint')
        coverage.append({'symbol': symbol, 'instrument_id': item['instrument_id'],
                         'first': item['candles'][0][0], 'last': item['candles'][-1][0]})
        observations = {x['zone_id']: x for x in result['observations']}
        contexts = {x['zone_id']: x for x in result['contexts']}
        if len(observations) != len(result['observations']) or len(contexts) != len(result['contexts']):
            raise ValueError('Ambiguous replay zone identity')
        for snapshot in result['snapshots']:
            zid = snapshot['zone_id']
            if zid not in observations or zid not in contexts:
                raise ValueError('Missing point-in-time evidence')
            row = list(_record(snapshot, observations[zid], contexts[zid]))
            # Storage identity only; analytical fields remain unchanged.
            row[0] = hashlib.sha256(f"{item['instrument_id']}|{snapshot['timeframe']}|{zid}|{snapshot['planning_timestamp']}".encode()).hexdigest()
            rows.append(tuple(row))
    if not rows or len(coverage) + len(exclusions) != status['target']:
        raise ValueError('Empty or incomplete evidence')
    version = f"dhan-evidence-{source['end']}-{digest[:12]}"
    metadata = {
        'historical_evidence_version': version, 'provider': 'dhan',
        'methodology_fingerprint': hashlib.sha256(json.dumps(METHODOLOGY_MANIFEST, sort_keys=True).encode()).hexdigest(),
        'methodology': METHODOLOGY_MANIFEST, 'dataset_period': {'start': source['start'], 'end': source['end']},
        'record_count': len(rows), 'trade_confidence_counts': {x: Counter(r[25] for r in rows)[x] for x in TC_LABELS},
        'source_universe': 'nse500', 'requested_symbols': status['target'],
        'processed_symbols': len(coverage), 'excluded_symbols': exclusions,
        'source_coverage': coverage, 'supported_timeframes': ['1D', '1W'],
        'source_sha256': digest, 'generated_from': 'persisted-dhan-point-in-time-replay',
        'coverage_note': 'Observation cutoff; individual instruments may have shorter histories. Recent zones have less follow-up. Current NSE 500 membership introduces survivorship bias.',
    }
    destination.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination, suffix='.sqlite3', delete=False) as file:
        temporary = Path(file.name)
    try:
        with closing(sqlite3.connect(temporary)) as connection:
            connection.executescript(SCHEMA)
            connection.executemany(INSERT, rows)
            connection.executemany('INSERT INTO metadata VALUES (?,?)', [(k, json.dumps(v)) for k,v in metadata.items()])
            connection.commit()
            if connection.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Artifact integrity failed')
        artifact = destination / f'{version}.sqlite3'
        if artifact.exists():
            raise ValueError('Immutable artifact already exists; no overwrite')
        temporary.replace(artifact)
        manifest = {'version': version, 'file': artifact.name, 'sha256': sha256(artifact)}
        pointer = destination / 'current-dhan-evidence.json'
        stage = pointer.with_suffix('.tmp')
        stage.write_text(json.dumps(manifest), encoding='utf-8')
        stage.replace(pointer)
        status.update(published=True, version=version, rows=len(rows))
        (directory / 'status.json').write_text(json.dumps(status), encoding='utf-8')
        return metadata
    finally:
        temporary.unlink(missing_ok=True)
