"""Resolve published Dhan evidence without mutating the frozen baseline."""
import hashlib
import json
from functools import lru_cache

from backend.historical_evidence.constants import PACKAGE_ROOT
from backend.historical_evidence.repository import HistoricalEvidenceRepository
from backend.historical_evidence.service import HistoricalEvidenceService


@lru_cache(maxsize=4)
def _load(filename, version, digest):
    if filename != f'{version}.sqlite3' or not version.startswith('dhan-evidence-') or '/' in filename or '\\' in filename:
        raise ValueError('Invalid evidence publication')
    path = PACKAGE_ROOT / 'data' / filename
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('Evidence artifact checksum mismatch')
    service = HistoricalEvidenceService(HistoricalEvidenceRepository(path), version=version)
    service.metadata(version)
    return service


def current_service():
    pointer = PACKAGE_ROOT / 'data' / 'current-dhan-evidence.json'
    if not pointer.exists():
        return None
    record = json.loads(pointer.read_text(encoding='utf-8'))
    return _load(record['file'], record['version'], record['sha256'])
