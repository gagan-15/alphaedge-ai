from __future__ import annotations

from datetime import UTC, datetime

from backend.services.market_data.dhan_index_quote_service import (
    DHAN_DASHBOARD_INDEXES,
    DhanIndexQuote,
)
from backend.services.market_data.market_snapshot_service import MarketSnapshotService


class _Universe:
    def get_symbols(self, universe: str, supplied_symbols=None):
        del universe, supplied_symbols
        return ["RELIANCE"]


class _DhanIndexes:
    def quotes(self):
        return {
            "nifty50": DhanIndexQuote(
                DHAN_DASHBOARD_INDEXES["nifty50"], 24000.0, 0.5,
                datetime.now(UTC).isoformat(),
            )
        }


def test_dhan_snapshot_uses_dhan_indexes_without_legacy_breadth(
    monkeypatch,
) -> None:
    import backend.services.market_data.market_snapshot_service as module

    monkeypatch.setattr(module, "MARKET_DATA_PROVIDER", "dhan")
    service = MarketSnapshotService(
        universe_service=_Universe(),  # type: ignore[arg-type]
        dhan_index_quotes=_DhanIndexes(),  # type: ignore[arg-type]
    )

    snapshot = service.get_snapshot()

    assert snapshot.source == "Dhan Market Quote API"
    assert snapshot.data_status == "live"
    assert snapshot.quotes["nifty50"].price == 24000.0
    assert snapshot.advancing == snapshot.declining == snapshot.unchanged == 0
