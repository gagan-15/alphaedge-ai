"""Resumable Dhan shadow bootstrap, validation, aggregation, and canonical scan."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from time import monotonic
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from backend.data_providers.dhan import DhanInstrument, DhanMarketDataProvider
from backend.data_providers.dhan.dhan_provider import DHAN_SOURCE_SEMANTICS
from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.services.market_data.dhan_shadow_store import (
    DhanShadowStore,
    ShadowMergeResult,
)
from backend.services.market_data.timeframe_service import aggregate_timeframe
from backend.validators.market_data_validator import MarketDataValidator

SHADOW_UNIVERSES = {
    "dhan_nse_main": ("NSE_MAIN",),
    "dhan_nse_sme": ("NSE_SME",),
    "dhan_bse_main": ("BSE_MAIN",),
    "dhan_bse_sme": ("BSE_SME",),
    "dhan_all_supported_indian_equity": ("NSE_MAIN", "NSE_SME", "BSE_MAIN", "BSE_SME"),
}


@dataclass(frozen=True)
class BootstrapReport:
    cohort: str
    requested: int
    completed: int
    failed: int
    retryable: int
    candles: int
    inserted: int
    corrected: int
    unchanged: int
    rejected: int
    elapsed_seconds: float


class DhanShadowService:
    def __init__(
        self, provider: DhanMarketDataProvider | None = None, store: DhanShadowStore | None = None
    ) -> None:
        self.provider = provider
        self.store = store or DhanShadowStore()

    def _require_provider(self) -> DhanMarketDataProvider:
        if self.provider is None:
            raise RuntimeError("A Dhan provider is required for this operation.")
        return self.provider

    def sync_master(self) -> dict[str, int]:
        instruments = self.provider.instrument_master(refresh=True)
        self.store.synchronize_master(instruments)
        categories = {key: 0 for key in ("NSE_MAIN", "NSE_SME", "BSE_MAIN", "BSE_SME")}
        for item in instruments:
            categories[item.category] += 1
        categories["TOTAL"] = len(instruments)
        categories["UNIQUE_ISIN"] = len({item.isin for item in instruments})
        exchanges_by_isin: dict[str, set[str]] = {}
        for item in instruments:
            exchanges_by_isin.setdefault(item.isin, set()).add(item.exchange)
        categories["CROSS_LISTED_ISIN"] = sum(
            len(exchanges) > 1 for exchanges in exchanges_by_isin.values()
        )
        return categories

    def universe(self, identity: str) -> tuple[DhanInstrument, ...]:
        categories = SHADOW_UNIVERSES[identity]
        return tuple(
            item
            for item in self._require_provider().instrument_master()
            if item.category in categories
        )

    def bootstrap_daily(
        self,
        cohort: str,
        *,
        limit: int | None = None,
        years: int = 10,
        final_attempt: bool = False,
    ) -> BootstrapReport:
        instruments = self.universe(cohort)[:limit]
        started = monotonic()
        totals = ShadowMergeResult()
        candles = completed = failed = retryable = 0
        end, start = date.today(), date.today() - timedelta(days=366 * years)
        for instrument in instruments:
            if self.store.complete(
                cohort,
                instrument.instrument_id,
                "1D",
                self.provider.source_semantics_version,
            ):
                completed += 1
                candles += len(self.store.load(instrument.instrument_id, "1D"))
                continue
            try:
                frame = self.provider.download_instrument_data(
                    instrument, start=start, end=end, interval="1d"
                )
                if frame.empty:
                    raise ValueError("NO_DATA")
                merge = self.store.merge(
                    instrument,
                    "1D",
                    "1d",
                    frame,
                    semantics=self.provider.source_semantics_version,
                )
                self.store.checkpoint(
                    cohort,
                    instrument,
                    "1D",
                    self.provider.source_semantics_version,
                    "COMPLETE",
                )
                completed += 1
                candles += len(frame)
                totals = ShadowMergeResult(
                    totals.inserted + merge.inserted,
                    totals.corrected + merge.corrected,
                    totals.unchanged + merge.unchanged,
                    totals.rejected + merge.rejected,
                )
            except Exception as error:  # isolated provider/data failure
                status = "FAILED" if final_attempt else "RETRYABLE"
                self.store.checkpoint(
                    cohort,
                    instrument,
                    "1D",
                    self.provider.source_semantics_version,
                    status,
                    error_code=type(error).__name__,
                )
                failed += status == "FAILED"
                retryable += status == "RETRYABLE"
        return BootstrapReport(
            cohort,
            len(instruments),
            completed,
            failed,
            retryable,
            candles,
            totals.inserted,
            totals.corrected,
            totals.unchanged,
            totals.rejected,
            monotonic() - started,
        )

    def refresh_daily(
        self,
        cohort: str,
        *,
        limit: int | None = None,
        overlap_days: int = 7,
    ) -> BootstrapReport:
        """Refresh only a correction overlap and newer Daily sessions."""

        instruments = self.universe(cohort)[:limit]
        started = monotonic()
        totals = ShadowMergeResult()
        candles = completed = failed = retryable = 0
        for instrument in instruments:
            persisted = self.store.load(instrument.instrument_id, "1D")
            if persisted.empty:
                retryable += 1
                continue
            start = persisted.index.max().date() - timedelta(days=overlap_days)
            try:
                frame = self.provider.download_instrument_data(
                    instrument,
                    start=start,
                    end=date.today(),
                    interval="1d",
                )
                merge = self.store.merge(
                    instrument,
                    "1D",
                    "1d",
                    frame,
                    semantics=self.provider.source_semantics_version,
                )
                completed += 1
                candles += len(frame)
                totals = ShadowMergeResult(
                    totals.inserted + merge.inserted,
                    totals.corrected + merge.corrected,
                    totals.unchanged + merge.unchanged,
                    totals.rejected + merge.rejected,
                )
            except Exception:
                retryable += 1
        return BootstrapReport(
            cohort,
            len(instruments),
            completed,
            failed,
            retryable,
            candles,
            totals.inserted,
            totals.corrected,
            totals.unchanged,
            totals.rejected,
            monotonic() - started,
        )

    def materialize_eod(
        self, instrument: DhanInstrument, timeframe: str
    ) -> ShadowMergeResult:
        daily = self.store.load(instrument.instrument_id, "1D")
        if daily.empty:
            raise ValueError("Daily shadow source is unavailable.")
        framed = aggregate_timeframe(daily, timeframe)
        return self.store.merge(
            instrument,
            timeframe,
            "1d",
            framed,
            semantics=(
                self.provider.source_semantics_version
                if self.provider is not None
                else DHAN_SOURCE_SEMANTICS
            ),
        )

    def materialize_eod_suffix(
        self, instrument: DhanInstrument, timeframe: str,
        earliest_daily_timestamp: object,
    ) -> ShadowMergeResult:
        """Update only aggregate buckets touched by a Daily source mutation.

        Calendar anchoring remains delegated to the existing deterministic
        ``aggregate_timeframe`` function.  The slice starts at a conservative
        canonical calendar boundary, so no bucket can be partial at its left
        edge and no complete historical aggregate is rebuilt.
        """
        if timeframe == "1D":
            return ShadowMergeResult()
        daily = self.store.load(instrument.instrument_id, "1D")
        if daily.empty:
            raise ValueError("Daily shadow source is unavailable.")
        stamp = pd.Timestamp(earliest_daily_timestamp)
        if stamp.tzinfo is not None and daily.index.tz is None:
            stamp = stamp.tz_localize(None)
        elif stamp.tzinfo is None and daily.index.tz is not None:
            stamp = stamp.tz_localize(daily.index.tz)
        # Start at the exact affected calendar bucket.  This preserves the
        # existing partial-bucket semantics while avoiding unrelated buckets.
        if timeframe == "1W":
            start = stamp.normalize() - pd.Timedelta(days=stamp.weekday())
        elif timeframe == "1M":
            start = stamp.normalize().replace(day=1)
        elif timeframe == "3M":
            quarter_month = ((stamp.month - 1) // 3) * 3 + 1
            start = stamp.normalize().replace(month=quarter_month, day=1)
        elif timeframe == "6M":
            half_month = 1 if stamp.month <= 6 else 7
            start = stamp.normalize().replace(month=half_month, day=1)
        else:  # 1Y
            start = stamp.normalize().replace(month=1, day=1)
        framed = aggregate_timeframe(daily.loc[daily.index >= start], timeframe)
        return self.store.merge(
            instrument, timeframe, "1d", framed,
            semantics=(
                self.provider.source_semantics_version
                if self.provider is not None else DHAN_SOURCE_SEMANTICS
            ),
        )

    def persisted_daily_canonical_universe(
        self, cohort: str,
    ) -> tuple[DhanInstrument, ...]:
        """Return the active Dhan Daily-success cohort without provider I/O.

        Higher EOD frames are derived exclusively from already persisted Daily
        candles.  Reading this local source-of-truth prevents a materializer
        from depending on a new instrument-master request or a live provider.
        """
        with self.store.connection() as connection:
            rows = connection.execute(
                """SELECT i.exchange,i.security_id,i.symbol,i.isin,i.series,
                          i.category,i.display_name
                   FROM dhan_instruments i
                   JOIN dhan_canonical_checkpoints c
                     ON c.instrument_id=i.instrument_id
                   LEFT JOIN dhan_active_zone_exclusions e
                     ON e.cohort=c.cohort AND e.instrument_id=c.instrument_id
                    AND e.timeframe='1D'
                   WHERE c.cohort=? AND c.timeframe='1D'
                     AND c.status='COMPLETE' AND i.provider_addressable=1
                     AND e.instrument_id IS NULL
                   ORDER BY i.instrument_id""",
                (cohort,),
            ).fetchall()
        return tuple(
            DhanInstrument(
                exchange=str(row["exchange"]), security_id=str(row["security_id"]),
                symbol=str(row["symbol"]), isin=str(row["isin"]),
                series=str(row["series"]), category=str(row["category"]),
                display_name=str(row["display_name"]),
            )
            for row in rows
        )

    def aggregate_intraday(
        self, instrument: DhanInstrument, source: pd.DataFrame, timeframe: str
    ) -> ShadowMergeResult:
        if timeframe not in {"75m", "125m"}:
            raise ValueError(
                "Only exact-session 75m and 125m shadow policies are approved."
            )
        framed = self.session_aggregate(source, timeframe)
        return self.store.merge(
            instrument,
            timeframe,
            "5m" if timeframe == "125m" else "15m",
            framed,
            semantics=self.provider.source_semantics_version,
        )

    @staticmethod
    def session_aggregate(source: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Aggregate exact Indian cash-session buckets without crossing sessions."""

        minutes = {"75m": 75, "125m": 125}.get(timeframe)
        if minutes is None:
            raise ValueError("Only 75m and 125m have an approved residual policy.")
        if source.empty:
            return source.copy()
        frame = source.copy().sort_index()
        index = pd.DatetimeIndex(frame.index)
        if index.tz is None:
            index = index.tz_localize("Asia/Kolkata")
        else:
            index = index.tz_convert("Asia/Kolkata")
        frame.index = index
        frame = frame.between_time("09:15", "15:29:59")
        pieces: list[pd.DataFrame] = []
        rule = f"{minutes}min"
        aggregations = {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
        if "Volume" in frame:
            aggregations["Volume"] = "sum"
        for _, session in frame.groupby(frame.index.date):
            if session.empty:
                continue
            session_open = session.index[0].normalize() + pd.Timedelta(
                hours=9, minutes=15
            )
            if session.index[0] != session_open:
                # A missing open is a data-quality break, not a shortened bucket.
                continue
            result = session.resample(rule, origin=session_open).agg(aggregations)
            result = result.dropna(subset=["Open", "High", "Low", "Close"])
            # The last bucket is accepted only when its source reaches the expected end.
            expected_ends = result.index + pd.Timedelta(minutes=minutes)
            complete = expected_ends <= session_open + pd.Timedelta(minutes=375)
            pieces.append(result.loc[complete])
        return pd.concat(pieces).sort_index() if pieces else frame.iloc[0:0]

    def canonical_zones(
        self, instrument: DhanInstrument, timeframe: str = "1D"
    ) -> list[object]:
        data = self.store.load(instrument.instrument_id, timeframe)
        zones: list[object] = []
        for segment in MarketDataValidator.validate_segments(data).segments:
            zones.extend(ZoneDetectionEngine().detect_zones(segment))
        return zones

    def materialize_daily_snapshot(self, cohort: str = "dhan_all_supported_indian_equity") -> dict[str, int]:
        """Run canonical detection over persisted Dhan Daily candles only."""
        instruments = self.universe(cohort)
        snapshot = self.store.begin_materialization(cohort, "1D", len(instruments))
        processed = zone_count = qualified = failures = 0
        for instrument in instruments:
            if self.store.canonical_complete(cohort, instrument.instrument_id, "1D"):
                processed += 1
                continue
            try:
                zones = self.canonical_zones(instrument, "1D")
                self.store.save_canonical(cohort, instrument, "1D", zones)
                zone_count += len(zones)
            except Exception as error:  # isolate one instrument
                failures += 1
                self.store.checkpoint(cohort, instrument, "1D", self.provider.source_semantics_version, "FAILED", error_code=type(error).__name__)
            processed += 1
        self.store.publish_materialization(snapshot, processed, zone_count, qualified)
        return {"snapshot_id": snapshot, "processed": processed, "failures": failures, "zones": zone_count, "qualified": qualified}

    def materialize_daily_snapshot_parallel(self, cohort: str = "dhan_all_supported_indian_equity", workers: int = 4) -> dict[str, int]:
        """Bounded parallel canonical processing with single-threaded persistence."""
        workers = max(1, min(int(workers), 6))
        instruments = [i for i in self.universe(cohort) if not self.store.canonical_complete(cohort, i.instrument_id, "1D")]
        snapshot = self.store.begin_materialization(cohort, "1D", len(self.universe(cohort)))
        processed = zones_total = failures = 0
        def calculate(instrument):
            return instrument, self.canonical_zones(instrument, "1D")
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="dhan-canonical") as pool:
            futures = [pool.submit(calculate, instrument) for instrument in instruments]
            for future in as_completed(futures):
                instrument = None
                try:
                    instrument, zones = future.result()
                    self.store.save_canonical(cohort, instrument, "1D", zones)
                    zones_total += len(zones)
                except Exception as error:
                    failures += 1
                    if instrument is not None:
                        self.store.checkpoint(cohort, instrument, "1D", self.provider.source_semantics_version, "FAILED", error_code=type(error).__name__)
                processed += 1
        self.store.publish_materialization(snapshot, processed, zones_total, 0)
        return {"snapshot_id": snapshot, "processed": processed, "failures": failures, "zones": zones_total, "qualified": 0, "workers": workers}

    def publish_daily_ready(self, cohort: str = "dhan_all_supported_indian_equity") -> dict[str, int]:
        """Atomically publish only a fully reconciled Dhan Daily cohort."""
        accounting = self.store.canonical_accounting(cohort, "1D")
        accepted = sum(accounting.get(key, 0) for key in ("SUCCESS", "NO_DATA", "QUARANTINED", "FAILED_PERMANENT"))
        if accepted != 7765:
            raise RuntimeError(f"Dhan Daily cohort is unresolved: {accepted}/7765")
        snapshot = self.store.begin_materialization(cohort, "1D", accepted)
        self.store.publish_materialization(snapshot, accounting["SUCCESS"], accounting["zones"], 0, "dhan-daily-persisted-v1")
        return {"snapshot_id": snapshot, **accounting}

    def publish_timeframe_ready(self, timeframe: str, cohort: str = "dhan_all_supported_indian_equity") -> dict[str, int]:
        accounting = self.store.canonical_accounting(cohort, timeframe)
        accepted = sum(accounting.get(key, 0) for key in ("SUCCESS", "NO_DATA", "QUARANTINED", "FAILED_PERMANENT"))
        if accepted != 7745:
            raise RuntimeError(f"Dhan {timeframe} cohort is unresolved: {accepted}/7745")
        snapshot = self.store.begin_materialization(cohort, timeframe, 7765)
        self.store.publish_materialization(snapshot, accounting["SUCCESS"], accounting["zones"], 0, f"dhan-{timeframe}-derived-v1")
        return {"snapshot_id": snapshot, **accounting}

    def rebuild_daily_structured_evidence(self, cohort: str = "dhan_all_supported_indian_equity", workers: int = 4) -> dict[str, int]:
        """Approved one-time rebuild from local Dhan candles into structured evidence."""
        workers = max(1, min(int(workers), 6))
        version = "structured-canonical-v1"
        instruments = [
            item for item in self.universe(cohort)
            if self.store.canonical_complete(cohort, item.instrument_id, "1D")
            and not self.store.structured_rebuild_complete(cohort, item.instrument_id, "1D", version)
        ]
        completed = failures = 0
        def calculate(item):
            return item, self.canonical_zones(item, "1D")
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="dhan-structured") as pool:
            futures = [pool.submit(calculate, item) for item in instruments]
            for future in as_completed(futures):
                try:
                    item, zones = future.result()
                    self.store.save_canonical(cohort, item, "1D", zones)
                    self.store.checkpoint_structured_rebuild(cohort, item.instrument_id, "1D", version)
                    completed += 1
                except Exception:
                    failures += 1
        return {"completed": completed, "failures": failures, "workers": workers}

    def rebuild_structured_evidence(
        self, timeframe: str, cohort: str = "dhan_all_supported_indian_equity", workers: int = 4
    ) -> dict[str, int]:
        """Replace only legacy canonical payloads with frozen typed JSON.

        Candles are read from the existing Dhan timeframe store.  This is a
        persistence-format repair, not a provider fetch or methodology change.
        """
        workers = max(1, min(int(workers), 6))
        with self.store.connection() as connection:
            rows = connection.execute(
                """SELECT i.exchange,i.security_id,i.symbol,i.isin,i.series,i.category,i.display_name
                FROM dhan_instruments i
                JOIN dhan_canonical_checkpoints c ON c.instrument_id=i.instrument_id
                JOIN dhan_shadow_zones z ON z.instrument_id=i.instrument_id
                    AND z.cohort=c.cohort AND z.timeframe=c.timeframe
                WHERE c.cohort=? AND c.timeframe=? AND c.status='COMPLETE'
                  AND i.provider_addressable=1
                  AND json_extract(z.payload, '$.zone_type') LIKE 'ZoneType.%'
                GROUP BY i.instrument_id
                ORDER BY i.instrument_id""",
                (cohort, timeframe),
            ).fetchall()
        instruments = [
            DhanInstrument(
                exchange=str(row["exchange"]), security_id=str(row["security_id"]),
                symbol=str(row["symbol"]), isin=str(row["isin"]), series=str(row["series"]),
                category=str(row["category"]), display_name=str(row["display_name"]),
            )
            for row in rows
        ]
        completed = failures = 0

        def calculate(item):
            return item, self.canonical_zones(item, timeframe)

        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix=f"dhan-structured-{timeframe}") as pool:
            futures = [pool.submit(calculate, item) for item in instruments]
            for future in as_completed(futures):
                try:
                    item, zones = future.result()
                    self.store.save_canonical(cohort, item, timeframe, zones)
                    completed += 1
                except Exception:
                    failures += 1
        return {"eligible": len(instruments), "completed": completed, "failures": failures, "workers": workers}

    def materialize_eod_snapshot_parallel(self, timeframe: str, cohort: str = "dhan_all_supported_indian_equity", workers: int = 4) -> dict[str, int]:
        """Derive and scan an EOD timeframe strictly from persisted Dhan Daily data."""
        workers = max(1, min(int(workers), 6))
        universe = self.persisted_daily_canonical_universe(cohort)
        candidates = [
            instrument for instrument in universe
            if not self.store.canonical_complete(cohort, instrument.instrument_id, timeframe)
        ]
        snapshot = self.store.begin_materialization(cohort, timeframe, len(universe))
        def calculate(instrument):
            self.materialize_eod(instrument, timeframe)
            return instrument, self.canonical_zones(instrument, timeframe)
        processed = zones_total = failures = 0
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix=f"dhan-{timeframe}") as pool:
            futures = {pool.submit(calculate, item): item for item in candidates}
            for future in as_completed(futures):
                instrument = futures[future]
                try:
                    instrument, zones = future.result()
                    self.store.save_canonical(cohort, instrument, timeframe, zones)
                    zones_total += len(zones)
                except Exception as error:
                    failures += 1
                    self.store.exclude_canonical(
                        cohort, instrument.instrument_id, timeframe,
                        "FAILED_PERMANENT",
                        f"PERSISTED_DAILY_DERIVATION_FAILED:{type(error).__name__}",
                    )
                processed += 1
        accounting = self.store.canonical_accounting(cohort, timeframe)
        accounted = sum(
            int(accounting.get(status, 0))
            for status in ("SUCCESS", "NO_DATA", "QUARANTINED", "FAILED_PERMANENT")
        )
        if accounted != len(universe):
            raise RuntimeError(
                f"Dhan {timeframe} persisted cohort is unresolved: "
                f"{accounted}/{len(universe)}"
            )
        self.store.publish_materialization(
            snapshot, accounted, accounting["zones"], 0,
            f"dhan-{timeframe}-derived-v1",
        )
        return {"snapshot_id": snapshot, "processed": accounted, "failures": failures, "zones": accounting["zones"], "workers": workers}
