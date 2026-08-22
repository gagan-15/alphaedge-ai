"""Maintained sector benchmark metadata loaded outside scanner logic."""

import json
from pathlib import Path


def _load_sector_benchmarks() -> dict[str, tuple[str, str]]:
    path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "universes"
        / "sector_benchmarks.json"
    )
    with path.open("r", encoding="utf-8") as source:
        payload = json.load(source)
    return {
        symbol: (values[0], values[1])
        for symbol, values in payload.get("symbols", {}).items()
    }


SECTOR_BENCHMARKS = _load_sector_benchmarks()

NIFTY_BENCHMARK = "^NSEI"
