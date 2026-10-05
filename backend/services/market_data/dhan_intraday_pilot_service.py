"""Bounded, Dhan-only intraday pilot materialization.

This service deliberately operates on ten current NSE identities only.  It
never reads or mutates EOD candles, canonical checkpoints, or snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from backend.data_providers.dhan import DhanInstrument, DhanMarketDataProvider
from backend.services.market_data.dhan_dashboard_enrichment_service import (
    DhanDashboardEnrichmentService,
)
from backend.services.market_data.dhan_shadow_service import DhanShadowService
from backend.services.market_data.dhan_shadow_store import DhanShadowStore


# The four intraday snapshots remain bounded to the pilot instruments, but use
# the production Dhan cohort key so the existing Dashboard read path can show
# the pilot without introducing a second routing model.
INTRADAY_PILOT_COHORT = "dhan_all_supported_indian_equity"
INTRADAY_PILOT_SYMBOLS = (
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY",
    "SBIN", "BHARTIARTL", "ITC", "LT", "HINDUNILVR",
)
INTRADAY_PILOT_TIMEFRAMES = ("15m", "75m", "125m", "1H")


@dataclass(frozen=True)
class IntradayPilotReport:
    instruments: int
    direct_15m_candles: int
    direct_5m_candles: int
    direct_1h_candles: int
    canonical_zones: dict[str, int]
    dashboard_rows: dict[str, int]
    exclusions: dict[str, int]


class DhanIntradayPilotService:
    """Create only the approved ten-instrument intraday pilot.

    15m and 1H are fetched directly from Dhan.  75m is derived from persisted
    15m and 125m from persisted 5m.  Derived bars use the existing exact NSE
    session aggregation, which rejects partial or cross-session bars.
    """

    def __init__(
        self,
        provider: DhanMarketDataProvider | None = None,
        store: DhanShadowStore | None = None,
    ) -> None:
        self.store = store or DhanShadowStore()
        self.provider = provider or DhanMarketDataProvider()
        self.shadow = DhanShadowService(
            provider=self.provider, store=self.store
        )

    def instruments(self) -> tuple[DhanInstrument, ...]:
        found: list[DhanInstrument] = []
        for symbol in INTRADAY_PILOT_SYMBOLS:
            identity = self.store.active_instrument_for_symbol(symbol)
            if identity is None or str(identity["exchange"]).upper() != "NSE":
                continue
            matches = self.store.instruments_by_ids([str(identity["instrument_id"])])
            if matches:
                found.append(matches[0])
        return tuple(found)

    def run(self, *, start: date | None = None, end: date | None = None) -> IntradayPilotReport:
        """Fetch a bounded pilot, persist it, then build pilot-only results."""

        end = end or date.today()
        start = start or end - timedelta(days=31)
        direct_15m = direct_5m = direct_1h = 0
        zones = {timeframe: 0 for timeframe in INTRADAY_PILOT_TIMEFRAMES}
        exclusions = {timeframe: 0 for timeframe in INTRADAY_PILOT_TIMEFRAMES}
        instruments = self.instruments()

        for instrument in instruments:
            try:
                frame_15m = self.provider.download_instrument_data(
                    instrument, start=start, end=end, interval="15m"
                )
                if frame_15m.empty:
                    raise ValueError("NO_15M_DATA")
                self.store.merge(instrument, "15m", "15m", frame_15m,
                                 semantics=self.provider.source_semantics_version)
                direct_15m += len(frame_15m)

                frame_5m = self.provider.download_instrument_data(
                    instrument, start=start, end=end, interval="5m"
                )
                if frame_5m.empty:
                    raise ValueError("NO_5M_DATA")
                self.store.merge(instrument, "5m", "5m", frame_5m,
                                 semantics=self.provider.source_semantics_version)
                direct_5m += len(frame_5m)

                frame_1h = self.provider.download_instrument_data(
                    instrument, start=start, end=end, interval="60m"
                )
                if frame_1h.empty:
                    raise ValueError("NO_1H_DATA")
                self.store.merge(instrument, "1H", "60m", frame_1h,
                                 semantics=self.provider.source_semantics_version)
                direct_1h += len(frame_1h)

                self.shadow.aggregate_intraday(instrument, frame_15m, "75m")
                self.shadow.aggregate_intraday(instrument, frame_5m, "125m")
                for timeframe in INTRADAY_PILOT_TIMEFRAMES:
                    detected = self.shadow.canonical_zones(instrument, timeframe)
                    self.store.save_canonical(
                        INTRADAY_PILOT_COHORT, instrument, timeframe, detected
                    )
                    zones[timeframe] += len(detected)
            except Exception as error:
                for timeframe in INTRADAY_PILOT_TIMEFRAMES:
                    if not self.store.canonical_complete(
                        INTRADAY_PILOT_COHORT, instrument.instrument_id, timeframe
                    ):
                        self.store.exclude_canonical(
                            INTRADAY_PILOT_COHORT, instrument.instrument_id,
                            timeframe, "FAILED_PERMANENT",
                            "INTRADAY_PILOT_PERSISTED_SOURCE_FAILED:"
                            f"{type(error).__name__}",
                        )
                        exclusions[timeframe] += 1

        rows: dict[str, int] = {}
        enrichment = DhanDashboardEnrichmentService(self.store)
        for timeframe in INTRADAY_PILOT_TIMEFRAMES:
            result = enrichment.materialize(timeframe, INTRADAY_PILOT_COHORT)
            rows[timeframe] = int(result["rows"])
        return IntradayPilotReport(
            instruments=len(instruments), direct_15m_candles=direct_15m,
            direct_5m_candles=direct_5m, direct_1h_candles=direct_1h,
            canonical_zones=zones, dashboard_rows=rows, exclusions=exclusions,
        )
