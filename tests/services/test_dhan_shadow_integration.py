from __future__ import annotations

from datetime import date
import json
from pathlib import Path

import pandas as pd

from backend.data_providers.dhan import DhanInstrument
from backend.services.market_data.dhan_shadow_service import DhanShadowService
from backend.services.market_data.dhan_shadow_store import DhanShadowStore


class FakeDhanProvider:
    source_semantics_version = "dhan-test-v1"

    def __init__(self, instruments: tuple[DhanInstrument, ...], frame: pd.DataFrame):
        self._instruments = instruments
        self._frame = frame
        self.calls = 0

    def instrument_master(self, *, refresh: bool = False):
        del refresh
        return self._instruments

    def download_instrument_data(
        self, instrument, *, start: date, end: date, interval: str
    ):
        del instrument, start, end, interval
        self.calls += 1
        return self._frame.copy()


def instrument(symbol: str = "TEST", security_id: str = "1") -> DhanInstrument:
    return DhanInstrument(
        "NSE", security_id, symbol, f"INE{security_id:0>9}", "EQ", "NSE_MAIN", symbol
    )


def daily_frame() -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=4, freq="D", tz="Asia/Kolkata")
    return pd.DataFrame(
        {
            "Open": [10, 11, 12, 13],
            "High": [12, 13, 14, 15],
            "Low": [9, 10, 11, 12],
            "Close": [11, 12, 13, 14],
            "Volume": [100, 110, 120, 130],
        },
        index=index,
    )


def test_shadow_store_keeps_source_identity_and_resumes(tmp_path: Path) -> None:
    provider = FakeDhanProvider((instrument(),), daily_frame())
    store = DhanShadowStore(tmp_path / "shadow.sqlite3")
    service = DhanShadowService(provider, store)  # type: ignore[arg-type]
    service.sync_master()

    first = service.bootstrap_daily("dhan_nse_main", limit=1)
    second = service.bootstrap_daily("dhan_nse_main", limit=1)

    assert first.completed == second.completed == 1
    assert first.inserted == 4
    assert second.inserted == 0
    assert provider.calls == 1
    assert len(store.load("NSE:1", "1D")) == 4


def test_incremental_refresh_reuses_old_history(tmp_path: Path) -> None:
    provider = FakeDhanProvider((instrument(),), daily_frame())
    store = DhanShadowStore(tmp_path / "shadow.sqlite3")
    service = DhanShadowService(provider, store)  # type: ignore[arg-type]
    service.sync_master()
    service.bootstrap_daily("dhan_nse_main", limit=1)

    result = service.refresh_daily("dhan_nse_main", limit=1)

    assert result.inserted == result.corrected == 0
    assert result.unchanged == 4
    assert len(store.load("NSE:1", "1D")) == 4


def test_exchange_listings_are_distinct(tmp_path: Path) -> None:
    items = (
        instrument("SHARED", "1"),
        DhanInstrument("BSE", "2", "SHARED", "INE000000001", "A", "BSE_MAIN", "Shared"),
    )
    store = DhanShadowStore(tmp_path / "shadow.sqlite3")
    store.synchronize_master(items)
    store.merge(items[0], "1D", "1d", daily_frame(), semantics="test")
    store.merge(items[1], "1D", "1d", daily_frame() * 2, semantics="test")
    assert store.load("NSE:1", "1D").iloc[0]["Close"] == 11
    assert store.load("BSE:2", "1D").iloc[0]["Close"] == 22


def test_dhan_master_counts_keep_nse_and_bse_universes_distinct(tmp_path: Path) -> None:
    records = (
        instrument("NSEMAIN", "1"),
        DhanInstrument("NSE", "2", "NSESME", "INE000000002", "SM", "NSE_SME", "NSE SME"),
        DhanInstrument("BSE", "3", "BSEMAIN", "INE000000003", "A", "BSE_MAIN", "BSE Main"),
        DhanInstrument("BSE", "4", "BSESME", "INE000000004", "M", "BSE_SME", "BSE SME"),
    )
    store = DhanShadowStore(tmp_path / "shadow.sqlite3")
    store.synchronize_master(records)

    counts = store.current_master_universe_counts({
        "nifty50": ["NSEMAIN"], "nifty100": ["NSEMAIN"],
        "nifty200": ["NSEMAIN"], "nse500": ["NSEMAIN"], "fno": ["NSEMAIN"],
    })

    assert counts["nse_main"] == counts["nse_sme"] == 1
    assert counts["allnse"] == 2
    assert counts["bse_main"] == counts["bse_sme"] == 1
    assert counts["allbse"] == 2
    assert counts["allindia"] == 4


def test_dashboard_rows_filter_by_exact_dhan_exchange_identity(tmp_path: Path) -> None:
    nse = instrument("SHARED", "1")
    bse = DhanInstrument("BSE", "2", "BSEONLY", "INE000000002", "A", "BSE_MAIN", "BSE Only")
    store = DhanShadowStore(tmp_path / "shadow.sqlite3")
    store.synchronize_master((nse, bse))
    snapshot = store.begin_dashboard_result_snapshot("cohort", "1D", 2, methodology_version="test")
    payload = '{"status":"APPROACHING"}'
    store.write_dashboard_result_rows(snapshot, [
        ("nse-row", nse.instrument_id, nse.symbol, "NSE", "DEMAND", "DBR", 80.0, 70.0, 1.0, True, payload),
        ("bse-row", bse.instrument_id, bse.symbol, "BSE", "DEMAND", "DBR", 80.0, 70.0, 1.0, True, payload),
    ])

    total, rows = store.query_dashboard_result_rows(
        snapshot, zone_type=None, pattern=None, min_zone_quality=None,
        min_trade_confidence=None, status=None, symbol=None, max_distance=None,
        sort="symbol", descending=False, page=1, page_size=10, universe="bse_main",
    )

    assert total == 1
    assert '"instrument_id":"BSE:2"' in rows[0]


def test_dashboard_numeric_distance_and_current_price_sorting_is_global(tmp_path: Path) -> None:
    first = instrument("FIRST", "1")
    second = instrument("SECOND", "2")
    third = instrument("THIRD", "3")
    store = DhanShadowStore(tmp_path / "shadow.sqlite3")
    store.synchronize_master((first, second, third))
    snapshot = store.begin_dashboard_result_snapshot("cohort", "1D", 3, methodology_version="test")
    store.write_dashboard_result_rows(snapshot, [
        ("first", first.instrument_id, first.symbol, "NSE", "DEMAND", "DBR", 80.0, 70.0, 0.0, True, '{"status":"IN ZONE","current_price":200.0}'),
        ("second", second.instrument_id, second.symbol, "NSE", "DEMAND", "DBR", 80.0, 70.0, 3.0, True, '{"status":"APPROACHING","current_price":50.0}'),
        ("third", third.instrument_id, third.symbol, "NSE", "DEMAND", "DBR", 80.0, 70.0, 1.0, True, '{"status":"APPROACHING","current_price":100.0}'),
    ])
    common = dict(
        snapshot_id=snapshot, zone_type=None, pattern=None, min_zone_quality=None,
        min_trade_confidence=None, status=None, symbol=None, max_distance=None,
        page_size=2, universe="allindia", universe_symbols=(),
    )

    total, nearest = store.query_dashboard_result_rows(
        **common, sort="distance", descending=False, page=1,
    )
    _, nearest_next = store.query_dashboard_result_rows(
        **common, sort="distance", descending=False, page=2,
    )
    assert total == 3
    assert [json.loads(row)["instrument_id"] for row in nearest + nearest_next] == [
        first.instrument_id, third.instrument_id, second.instrument_id,
    ]

    _, expensive = store.query_dashboard_result_rows(
        **common, sort="current_price", descending=True, page=1,
    )
    assert [json.loads(row)["instrument_id"] for row in expensive] == [
        first.instrument_id, third.instrument_id,
    ]


def test_dhan_master_search_includes_bse_without_dashboard_rows(tmp_path: Path) -> None:
    bse = DhanInstrument("BSE", "2", "BSEONLY", "INE000000002", "A", "BSE_MAIN", "BSE Only")
    store = DhanShadowStore(tmp_path / "shadow.sqlite3")
    store.synchronize_master((bse,))

    found = store.search_current_instruments("BSEONLY")

    assert found[0]["instrument_id"] == "BSE:2"
    assert found[0]["exchange"] == "BSE"


def test_75m_and_125m_are_session_anchored() -> None:
    index = pd.date_range(
        "2026-08-20 09:15", periods=75, freq="5min", tz="Asia/Kolkata"
    )
    source = pd.DataFrame(
        {
            "Open": range(75),
            "High": range(1, 76),
            "Low": range(75),
            "Close": range(1, 76),
            "Volume": [1] * 75,
        },
        index=index,
    )
    seventy_five = DhanShadowService.session_aggregate(source, "75m")
    one_twenty_five = DhanShadowService.session_aggregate(source, "125m")
    assert len(seventy_five) == 5
    assert len(one_twenty_five) == 3
    assert seventy_five.index[0].hour == 9 and seventy_five.index[0].minute == 15


def test_missing_session_open_is_not_fabricated() -> None:
    source = daily_frame()
    source.index = pd.date_range(
        "2026-08-20 09:20", periods=4, freq="5min", tz="Asia/Kolkata"
    )
    assert DhanShadowService.session_aggregate(source, "75m").empty


def test_duplicate_identical_candles_are_collapsed(tmp_path: Path) -> None:
    store = DhanShadowStore(tmp_path / "shadow.sqlite3")
    store.synchronize_master((instrument(),))
    frame = daily_frame()
    frame = pd.concat([frame, frame.iloc[[1]]])
    result = store.merge(instrument(), "1D", "1d", frame, semantics="test")
    assert result.inserted == 4
    assert result.rejected == 0
    assert len(store.load("NSE:1", "1D")) == 4


def test_duplicate_conflicts_are_recorded_and_excluded(tmp_path: Path) -> None:
    store = DhanShadowStore(tmp_path / "shadow.sqlite3")
    store.synchronize_master((instrument(),))
    frame = daily_frame()
    conflicting = frame.iloc[[1]].copy()
    conflicting.iloc[0, conflicting.columns.get_loc("Close")] = 99
    frame = pd.concat([frame, conflicting])
    result = store.merge(instrument(), "1D", "1d", frame, semantics="test")
    assert result.inserted == 3
    assert result.rejected == 2
    with store.connection() as connection:
        conflict = connection.execute(
            "SELECT row_count FROM dhan_shadow_data_quality_conflicts"
        ).fetchone()
    assert conflict["row_count"] == 2
    assert len(store.load("NSE:1", "1D")) == 3
