"""Market-universe symbol provider used by every scanner entry point."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

UniverseName = Literal[
    "nifty50",
    "nifty100",
    "nifty200",
    "nse500",
    "fno",
    "allnse",
    "watchlist",
    "custom",
]

PREDEFINED_UNIVERSES = {
    "nifty50",
    "nifty100",
    "nifty200",
    "nse500",
    "fno",
    "allnse",
}


class UniverseService:
    """Resolve a universe without exposing its storage to scanner code."""

    def __init__(self, data_directory: Path | None = None) -> None:
        self._data_directory = data_directory or (
            Path(__file__).resolve().parents[2] / "data" / "universes"
        )

    def get_symbols(
        self,
        universe: UniverseName = "nse500",
        supplied_symbols: list[str] | tuple[str, ...] | None = None,
    ) -> list[str]:
        normalized_universe = universe.lower()
        if normalized_universe in {"watchlist", "custom"}:
            return self._normalize_symbols(supplied_symbols or ())
        if normalized_universe not in PREDEFINED_UNIVERSES:
            raise ValueError(f"Unsupported market universe: {universe}")
        return list(
            self._load_predefined(
                str(self._data_directory),
                normalized_universe,
            )
        )

    @staticmethod
    def _normalize_symbols(symbols: list[str] | tuple[str, ...]) -> list[str]:
        return sorted(
            {symbol.strip().upper() for symbol in symbols if symbol and symbol.strip()}
        )

    @staticmethod
    @lru_cache(maxsize=8)
    def _load_predefined(
        data_directory: str,
        universe: str,
    ) -> tuple[str, ...]:
        path = Path(data_directory) / f"{universe}.json"
        with path.open("r", encoding="utf-8-sig") as source:
            payload = json.load(source)
        symbols = UniverseService._normalize_symbols(payload.get("symbols", ()))
        if not symbols:
            raise ValueError(f"Universe file contains no symbols: {path.name}")
        return tuple(symbols)
