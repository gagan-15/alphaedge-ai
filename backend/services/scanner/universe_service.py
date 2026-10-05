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
    "nse_main",
    "allnse",
    "nse_sme",
    "bse_main",
    "bse_sme",
    "allbse",
    "allindia",
    "watchlist",
    "custom",
]

PREDEFINED_UNIVERSES = {
    "nifty50",
    "nifty100",
    "nifty200",
    "nse500",
    "fno",
    "nse_main",
    "allnse",
    "nse_sme",
    "bse_main",
    "bse_sme",
    "allbse",
    "allindia",
}


class UniverseService:
    """Resolve a universe without exposing its storage to scanner code."""

    def __init__(self, data_directory: Path | None = None) -> None:
        self._use_persistent_master = data_directory is None
        self._data_directory = data_directory or (
            Path(__file__).resolve().parents[2] / "data" / "universes"
        )

    def get_symbols(
        self,
        universe: UniverseName = "allnse",
        supplied_symbols: list[str] | tuple[str, ...] | None = None,
    ) -> list[str]:
        normalized_universe = universe.lower()
        if normalized_universe in {"watchlist", "custom"}:
            return self._normalize_symbols(supplied_symbols or ())
        if normalized_universe not in PREDEFINED_UNIVERSES:
            raise ValueError(f"Unsupported market universe: {universe}")
        # BSE and explicit Dhan categories are resolved by Dhan's persisted
        # instrument master on the Dhan Dashboard path. They have no Yahoo
        # JSON fallback and therefore must never be silently substituted.
        if normalized_universe in {"nse_main", "bse_main", "bse_sme", "allbse"}:
            if normalized_universe == "nse_main":
                normalized_universe = "allnse"
            else:
                raise ValueError(
                    f"The {normalized_universe} universe requires the Dhan instrument master."
                )
        persistent_universes = {"allnse", "nse_sme", "allindia"}
        if (
            normalized_universe in persistent_universes
            and self._use_persistent_master
        ):
            # The synchronized persistent NSE Main Equity master is the
            # canonical runtime source. The versioned JSON remains only a
            # bootstrap fallback before the first successful synchronization.
            from backend.services.scanner.instrument_master_service import (
                InstrumentMasterService,
            )

            master = InstrumentMasterService()
            if master.has_current_master(normalized_universe):
                symbols = master.active_symbols(normalized_universe)
                if symbols:
                    return symbols
            if (
                normalized_universe == "allindia"
                and master.has_current_master("allnse")
            ):
                # Last-known-good fallback during the first NSE SME sync.
                return master.active_symbols("allnse")
            if normalized_universe != "allnse":
                raise ValueError(
                    f"The synchronized {normalized_universe} instrument master "
                    "is not ready."
                )
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
