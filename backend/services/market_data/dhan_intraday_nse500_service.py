"""Resumable Dhan-only intraday rollout for the approved NSE 500 scope."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, timedelta

from backend.data_providers.dhan import DhanInstrument, DhanMarketDataProvider
from backend.services.market_data.dhan_shadow_service import DhanShadowService
from backend.services.market_data.dhan_shadow_store import DhanShadowStore
from backend.services.scanner.universe_service import UniverseService


INTRADAY_NSE500_COHORT = "dhan_intraday_nse500"
_SOURCE_FRAMES = (("5m", "5m"), ("15m", "15m"), ("1H", "60m"))
_CANONICAL_FRAMES = ("15m", "75m", "125m", "1H")
_WINDOW_DAYS = 90


@dataclass(frozen=True)
class IntradayNse500Report:
    target: int
    completed: int
    retryable: int
    skipped: int
    canonical_zones: int


class DhanIntradayNse500Service:
    """Incrementally prepare the approved one-year NSE 500 intraday cohort.

    It persists only the minimum direct Dhan sources (5m, 15m, 60m).  75m and
    125m are always deterministic local session aggregates and need no extra
    provider requests.
    """

    def __init__(
        self,
        provider: DhanMarketDataProvider | None = None,
        store: DhanShadowStore | None = None,
    ) -> None:
        self.store = store or DhanShadowStore()
        self.provider = provider or DhanMarketDataProvider()
        self.shadow = DhanShadowService(provider=self.provider, store=self.store)

    def instruments(self) -> tuple[DhanInstrument, ...]:
        resolved: list[DhanInstrument] = []
        for symbol in UniverseService().get_symbols("nse500"):
            row = self.store.active_instrument_for_symbol(symbol)
            if row is None or str(row["exchange"]).upper() != "NSE":
                continue
            matches = self.store.instruments_by_ids([str(row["instrument_id"])])
            if matches:
                resolved.append(matches[0])
        return tuple(resolved)

    @staticmethod
    def _windows(start: date, end: date) -> tuple[tuple[date, date], ...]:
        windows: list[tuple[date, date]] = []
        cursor = start
        while cursor < end:
            upper = min(cursor + timedelta(days=_WINDOW_DAYS), end)
            windows.append((cursor, upper))
            cursor = upper
        return tuple(windows)

    def _source_complete(self, instrument: DhanInstrument) -> bool:
        return all(
            self.store.complete(
                INTRADAY_NSE500_COHORT,
                instrument.instrument_id,
                timeframe,
                self.provider.source_semantics_version,
            )
            for timeframe, _ in _SOURCE_FRAMES
        )

    def _download_source(
        self, instrument: DhanInstrument, timeframe: str, interval: str,
        start: date, end: date,
    ) -> None:
        if self.store.complete(
            INTRADAY_NSE500_COHORT, instrument.instrument_id, timeframe,
            self.provider.source_semantics_version,
        ):
            return
        received = False
        for lower, upper in self._windows(start, end):
            frame = self.provider.download_instrument_data(
                instrument, start=lower, end=upper, interval=interval
            )
            if frame.empty:
                continue
            received = True
            self.store.merge(
                instrument, timeframe, interval, frame,
                semantics=self.provider.source_semantics_version,
            )
        if not received:
            raise ValueError(f"NO_{timeframe.upper()}_INTRADAY_DATA")
        self.store.checkpoint(
            INTRADAY_NSE500_COHORT, instrument, timeframe,
            self.provider.source_semantics_version, "COMPLETE",
        )

    def _process(self, instrument: DhanInstrument, start: date, end: date) -> int:
        for timeframe, interval in _SOURCE_FRAMES:
            self._download_source(instrument, timeframe, interval, start, end)
        self.shadow.aggregate_intraday(
            instrument, self.store.load(instrument.instrument_id, "15m"), "75m"
        )
        self.shadow.aggregate_intraday(
            instrument, self.store.load(instrument.instrument_id, "5m"), "125m"
        )
        zones_total = 0
        for timeframe in _CANONICAL_FRAMES:
            if self.store.canonical_complete(
                INTRADAY_NSE500_COHORT, instrument.instrument_id, timeframe
            ):
                continue
            zones = self.shadow.canonical_zones(instrument, timeframe)
            self.store.save_canonical(
                INTRADAY_NSE500_COHORT, instrument, timeframe, zones
            )
            zones_total += len(zones)
        return zones_total

    def run(
        self, *, years: int = 1, workers: int = 4,
        limit: int | None = None,
    ) -> IntradayNse500Report:
        """Resume the approved cohort without touching EOD data or snapshots."""

        workers = max(1, min(int(workers), 4))
        end = date.today()
        start = end - timedelta(days=366 * years)
        universe = self.instruments()
        if limit is not None:
            universe = universe[:max(0, limit)]
        pending = [item for item in universe if not self._source_complete(item)]
        completed = len(universe) - len(pending)
        retryable = canonical_zones = 0

        with ThreadPoolExecutor(
            max_workers=workers, thread_name_prefix="dhan-intraday"
        ) as pool:
            futures = {
                pool.submit(self._process, item, start, end): item
                for item in pending
            }
            for future in as_completed(futures):
                instrument = futures[future]
                try:
                    canonical_zones += future.result()
                    completed += 1
                except Exception as error:
                    retryable += 1
                    for timeframe, _ in _SOURCE_FRAMES:
                        self.store.checkpoint(
                            INTRADAY_NSE500_COHORT, instrument, timeframe,
                            self.provider.source_semantics_version, "RETRYABLE",
                            error_code=type(error).__name__,
                        )
        return IntradayNse500Report(
            target=len(universe), completed=completed, retryable=retryable,
            skipped=len(universe) - len(pending), canonical_zones=canonical_zones,
        )
