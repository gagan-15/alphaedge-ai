"""Checkpointed, offline Dhan evidence replay. Never modifies production data.

Outputs research shards only. Publication requires a separate validated read
model; the frozen Milestone 9C artifact is never overwritten by this command.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sqlite3
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from backend.core.logger import logger

from backend.services.scanner.universe_service import UniverseService
from backend.validators.market_data_validator import MarketDataValidator
from scripts.audit.run_large_scale_context_validation import _run_symbol


def atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, default=str), encoding='utf-8')
    temporary.replace(path)


class PersistedSource:
    def __init__(self, frame):
        self.frame = frame

    def get_stock_data_segments(self, symbol, period, interval):
        return MarketDataValidator.validate_segments(self.frame)


def capture(database: Path, output: Path, start: str, end: str, symbols: list[str]):
    """Capture all inputs in one read transaction, with exact NSE identities."""
    with sqlite3.connect(f'file:{database.resolve().as_posix()}?mode=ro', uri=True) as connection:
        connection.execute('BEGIN')
        captured = {}
        for symbol in symbols:
            matches = connection.execute(
                "SELECT instrument_id,isin FROM dhan_instruments WHERE exchange='NSE' AND symbol=? AND provider_addressable=1",
                (symbol,),
            ).fetchall()
            if len(matches) != 1:
                captured[symbol] = {
                    'instrument_id': None, 'isin': None, 'candles': [],
                    'exclusion_reason': 'DHAN_IDENTITY_UNAVAILABLE' if not matches else 'DHAN_IDENTITY_AMBIGUOUS',
                }
                continue
            identity, isin = matches[0]
            rows = connection.execute(
                "SELECT timestamp,open,high,low,close,volume FROM dhan_shadow_candles WHERE instrument_id=? AND timeframe='1D' AND provider='dhan' AND timestamp>=? AND timestamp<? ORDER BY timestamp",
                (identity, start, str((pd.Timestamp(end) + pd.Timedelta(days=1)).date())),
            ).fetchall()
            captured[symbol] = {'instrument_id': identity, 'isin': isin, 'candles': rows}
        payload = {'provider': 'dhan', 'start': start, 'end': end, 'symbols': captured}
        atomic_json(output, payload)
    return payload


def replay_item(symbol, item, start, end, digest):
    logger.setLevel(logging.WARNING)
    if not item['candles']:
        return dict(status='EXCLUDED', reason=item.get('exclusion_reason', 'NO_PERSISTED_DHAN_HISTORY'),
                    symbol=symbol, instrument_id=item['instrument_id'], source_sha256=digest)
    frame = pd.DataFrame(item['candles'], columns=['timestamp','Open','High','Low','Close','Volume'])
    frame.index = pd.DatetimeIndex(pd.to_datetime(frame.pop('timestamp'), utc=True)).tz_convert('Asia/Kolkata')
    try:
        result = _run_symbol(PersistedSource(frame), symbol, start=start, end=end)
    except Exception as error:
        result = {'status': 'FAILED', 'error': type(error).__name__}
    result.update(symbol=symbol, instrument_id=item['instrument_id'], source_sha256=digest)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', type=Path, default=Path('backend/data/shadow/dhan-shadow.sqlite3'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--start', default='2021-08-18')
    parser.add_argument('--end', required=True)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--workers', type=int, choices=range(1,5), default=2)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    logger.setLevel(logging.WARNING)
    start, end = pd.Timestamp(args.start), pd.Timestamp(args.end)
    if start > end:
        raise ValueError('Invalid period')
    args.output.mkdir(parents=True, exist_ok=True)
    symbols = UniverseService().get_symbols('nse500')
    if args.limit:
        symbols = symbols[:args.limit]
    source_path = args.output / 'dhan-inputs.json'
    source = (json.loads(source_path.read_text(encoding='utf-8')) if source_path.exists()
              else capture(args.database, source_path, args.start, args.end, symbols))
    if source['start'] != args.start or source['end'] != args.end or list(source['symbols']) != symbols:
        raise ValueError('Resume input manifest mismatch')
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    pending = []
    for index, symbol in enumerate(symbols, 1):
        checkpoint = args.output / f'replay-{index:04d}.json'
        if checkpoint.exists():
            saved = json.loads(checkpoint.read_text(encoding='utf-8'))
            if saved.get('source_sha256') != digest or saved.get('symbol') != symbol:
                raise ValueError('Replay checkpoint identity mismatch')
            if saved.get('status') in {'PROCESSED', 'EXCLUDED'}:
                continue
        pending.append((checkpoint, symbol))
    done = len(symbols) - len(pending)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(replay_item, symbol, source['symbols'][symbol], start, end, digest): (checkpoint, symbol)
                   for checkpoint, symbol in pending}
        for future in as_completed(futures):
            checkpoint, symbol = futures[future]
            result = future.result()
            atomic_json(checkpoint, result)
            done += 1
            atomic_json(args.output / 'progress.json', {'completed': done, 'total': len(symbols), 'end': args.end})
            print(json.dumps({'completed': done, 'total': len(symbols), 'symbol': symbol, 'status': result['status']}), flush=True)
    statuses = [json.loads((args.output / f'replay-{i:04d}.json').read_text(encoding='utf-8'))['status'] for i in range(1,len(symbols)+1)]
    atomic_json(args.output / 'status.json', {
        'state': 'REPLAY_COMPLETE' if all(x in {'PROCESSED', 'EXCLUDED'} for x in statuses) else 'REPLAY_INCOMPLETE',
        'target': len(symbols), 'processed': statuses.count('PROCESSED'),
        'failed': statuses.count('FAILED'), 'end': args.end,
        'excluded': statuses.count('EXCLUDED'),
        'source_sha256': digest, 'published': False,
    })
    if args.publish:
        if args.limit:
            raise ValueError('Sample replays cannot be published')
        from scripts.audit.publish_dhan_historical_evidence import publish
        publish(args.output)


if __name__ == '__main__':
    main()
