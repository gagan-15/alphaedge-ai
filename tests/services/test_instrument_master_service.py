from __future__ import annotations

import hashlib

import pytest

from backend.services.scanner.instrument_master_service import (
    InstrumentMasterService,
)
from backend.services.scanner.persistent_scanner_store import PersistentScannerStore


def _csv(*rows: str) -> bytes:
    header = (
        "SYMBOL,NAME OF COMPANY,SERIES,DATE OF LISTING,PAID UP VALUE,"
        "MARKET LOT,ISIN NUMBER,FACE VALUE\n"
    )
    return (header + "\n".join(rows)).encode()


def _sme_csv(*rows: str) -> bytes:
    header = (
        "SYMBOL,NAME_OF_COMPANY,SERIES,DATE_OF_LISTING,PAID_UP_VALUE,"
        "ISIN_NUMBER,FACE_VALUE\n"
    )
    return (header + "\n".join(rows)).encode()


def test_sync_reconciles_by_isin_and_preserves_symbol_alias(tmp_path) -> None:
    path = tmp_path / "scanner.sqlite3"
    PersistentScannerStore(path)
    service = InstrumentMasterService(path)
    first = _csv("OLD,Example Limited,EQ,01-JAN-2020,1,1,INE000A01001,1")
    second = _csv("NEW,Example Limited,EQ,01-JAN-2020,1,1,INE000A01001,1")

    service.synchronize(
        service.parse_main_equity(first),
        source="test",
        source_checksum=hashlib.sha256(first).hexdigest(),
    )
    service.synchronize(
        service.parse_main_equity(second),
        source="test",
        source_checksum=hashlib.sha256(second).hexdigest(),
        symbol_changes=(("OLD", "NEW", "01-JAN-2026"),),
    )

    assert service.active_symbols() == ["NEW"]
    result = service.search("OLD")[0]
    assert result["instrument_id"] == "NSE:OLD"
    assert result["exchange_symbol"] == "NEW"


def test_sync_marks_stale_inactive_without_deleting_identity(tmp_path) -> None:
    path = tmp_path / "scanner.sqlite3"
    PersistentScannerStore(path)
    service = InstrumentMasterService(path)
    initial = _csv(
        "KEEP,Keep Limited,EQ,01-JAN-2020,1,1,INE000A01001,1",
        "STALE,Stale Limited,BE,01-JAN-2020,1,1,INE000A01002,1",
    )
    current = _csv("KEEP,Keep Limited,EQ,01-JAN-2020,1,1,INE000A01001,1")
    service.synchronize(
        service.parse_main_equity(initial), source="test", source_checksum="one"
    )
    result = service.synchronize(
        service.parse_main_equity(current), source="test", source_checksum="two"
    )

    assert result["inactive_count"] == 1
    assert service.active_symbols() == ["KEEP"]
    assert service.search("STALE") == []


def test_invalid_source_cannot_replace_last_known_good(tmp_path) -> None:
    path = tmp_path / "scanner.sqlite3"
    PersistentScannerStore(path)
    service = InstrumentMasterService(path)
    valid = _csv("SAFE,Safe Limited,BZ,01-JAN-2020,1,1,INE000A01001,1")
    service.synchronize(
        service.parse_main_equity(valid), source="test", source_checksum="safe"
    )

    with pytest.raises(ValueError):
        service.parse_main_equity(b"SYMBOL,NAME OF COMPANY,SERIES,ISIN NUMBER\n")

    assert service.active_symbols() == ["SAFE"]


def test_stale_sync_respects_cross_process_lease(tmp_path) -> None:
    path = tmp_path / "scanner.sqlite3"
    PersistentScannerStore(path)
    first = InstrumentMasterService(path)
    second = InstrumentMasterService(path)

    assert first._try_claim_sync() is True
    assert second.synchronize_if_stale() == {"status": "ALREADY_RUNNING"}
    first._finish_sync_claim()


def test_coverage_does_not_claim_unvalidated_markets(tmp_path) -> None:
    path = tmp_path / "scanner.sqlite3"
    PersistentScannerStore(path)
    service = InstrumentMasterService(path)
    payload = _csv("SAFE,Safe Limited,EQ,01-JAN-2020,1,1,INE000A01001,1")
    service.synchronize(
        service.parse_main_equity(payload), source="test", source_checksum="safe"
    )

    capabilities = {item["id"]: item for item in service.coverage_capabilities()}

    assert capabilities["allnse"]["state"] == "READY"
    assert capabilities["allnse"]["instrument_count"] == 1
    assert capabilities["bse_main"]["state"] == "PROVIDER_DEPENDENT"
    assert capabilities["bse_main"]["instrument_count"] == 0
    assert capabilities["nse_sme"]["state"] == "UNAVAILABLE"


def test_sme_master_and_supported_union_remain_separate(tmp_path) -> None:
    path = tmp_path / "scanner.sqlite3"
    PersistentScannerStore(path)
    service = InstrumentMasterService(path)
    main = _csv("MAIN,Main Limited,EQ,01-JAN-2020,1,1,INE000A01001,1")
    sme = _sme_csv("SMALL,Small Limited,SM,01-JAN-2020,1,INE000A01002,1")

    service.synchronize(
        service.parse_main_equity(main), source="main", source_checksum="main"
    )
    service._synchronize_universe(
        service.parse_sme_equity(sme),
        universe="nse_sme",
        instrument_type="SME_EQUITY",
        scope="NSE SME Equity (SM, ST, SZ)",
        allowed_series=frozenset({"SM", "ST", "SZ"}),
        source="sme",
        source_checksum="sme",
    )
    service._publish_supported_indian_equity_union()

    assert service.active_symbols("allnse") == ["MAIN"]
    assert service.active_symbols("nse_sme") == ["SMALL"]
    assert service.active_symbols("allindia") == ["MAIN", "SMALL"]
