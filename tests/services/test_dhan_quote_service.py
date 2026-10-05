from __future__ import annotations

from backend.data_providers.dhan import (
    DhanInstrument,
    DhanLiveQuote,
    DhanMarketDataProvider,
)
from backend.services.market_data.dhan_index_quote_service import (
    DHAN_DASHBOARD_INDEXES,
    DhanIndexQuoteService,
)
from backend.services.market_data.dhan_quote_service import DhanQuoteService


def _instrument(security_id: str = "11536") -> DhanInstrument:
    return DhanInstrument(
        "NSE", security_id, "RELIANCE", "INE002A01018", "EQ", "NSE_MAIN", "RELIANCE"
    )


class _QuoteProvider:
    def __init__(self) -> None:
        self.calls = 0

    def latest_quotes(self, instruments: list[DhanInstrument]):
        self.calls += 1
        return {
            item.instrument_id: DhanLiveQuote(123.45, "2026-08-30T09:15:00+00:00")
            for item in instruments
        }


def test_quote_service_caches_exact_instrument_identity() -> None:
    instrument = _instrument()
    provider = _QuoteProvider()
    service = DhanQuoteService(
        provider=provider, ttl_seconds=60  # type: ignore[arg-type]
    )

    first = service.quotes_for([instrument])
    second = service.quotes_for([instrument])

    assert first[instrument.instrument_id].price == 123.45
    assert second[instrument.instrument_id].as_of == "2026-08-30T09:15:00+00:00"
    assert provider.calls == 1


class _Response:
    status_code = 200
    headers: dict[str, str] = {}

    def __init__(self, body: dict) -> None:
        self._body = body

    def json(self) -> dict:
        return self._body


class _Session:
    def __init__(self) -> None:
        self.posts: list[dict] = []

    def post(self, url: str, *, headers: dict, json: dict, timeout: int):
        del url, headers, timeout
        self.posts.append(json)
        return _Response({"data": {"NSE_EQ": {"11536": {"last_price": 1412.5}}}})


def test_latest_quotes_uses_exact_dhan_security_id_and_segment() -> None:
    session = _Session()
    provider = DhanMarketDataProvider(
        access_token="test-token",
        client_id="test-client",
        session=session,  # type: ignore[arg-type]
    )

    quotes = provider.latest_quotes([_instrument()])

    assert session.posts == [{"NSE_EQ": [11536]}]
    assert quotes["NSE:11536"].price == 1412.5


class _IndexQuoteProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, tuple[str, str]]] = []

    def latest_market_quotes(self, identities: dict[str, tuple[str, str]]):
        from backend.data_providers.dhan import DhanMarketQuote

        self.calls.append(identities)
        return {
            key: DhanMarketQuote(
                price=100.0 + index,
                net_change=1.0,
                previous_close=99.0 + index,
                as_of="2026-08-31T09:15:00+00:00",
            )
            for index, key in enumerate(identities)
        }


def test_index_quote_service_uses_verified_dhan_index_identities() -> None:
    provider = _IndexQuoteProvider()
    service = DhanIndexQuoteService(provider=provider)  # type: ignore[arg-type]

    quotes = service.quotes()

    assert provider.calls == [{
        "nifty50": ("IDX_I", "13"),
        "sensex": ("IDX_I", "51"),
        "bank_nifty": ("IDX_I", "25"),
        "india_vix": ("IDX_I", "21"),
    }]
    assert set(quotes) == set(DHAN_DASHBOARD_INDEXES)
    assert quotes["nifty50"].change_percent == 1.0 / 99.0 * 100


class _MarketQuoteSession:
    def __init__(self) -> None:
        self.posts: list[dict] = []

    def post(self, url: str, *, headers: dict, json: dict, timeout: int):
        del url, headers, timeout
        self.posts.append(json)
        return _Response({
            "data": {
                "IDX_I": {
                    "13": {"last_price": 24000.0, "net_change": 120.0},
                    "51": {"last_price": 77000.0, "net_change": -200.0},
                }
            }
        })


def test_latest_market_quotes_uses_index_segment_and_derives_previous_close() -> None:
    session = _MarketQuoteSession()
    provider = DhanMarketDataProvider(
        access_token="test-token",
        client_id="test-client",
        session=session,  # type: ignore[arg-type]
    )

    quotes = provider.latest_market_quotes({
        "nifty50": ("IDX_I", "13"),
        "sensex": ("IDX_I", "51"),
    })

    assert session.posts == [{"IDX_I": [13, 51]}]
    assert quotes["nifty50"].previous_close == 23880.0
    assert quotes["sensex"].previous_close == 77200.0
