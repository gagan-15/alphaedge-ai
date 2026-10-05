"""Read-only DhanHQ adapter used exclusively by the shadow data pipeline."""

from __future__ import annotations

import os
import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from threading import Lock
from time import monotonic, sleep

import pandas as pd
import requests
from pandas import DataFrame

from backend.data_providers.base_market_data_provider import BaseMarketDataProvider
from backend.services.market_data.dhan_authentication_service import (
    DhanAuthenticationError,
    DhanAuthenticationService,
)

DHAN_API_ROOT = "https://api.dhan.co/v2"
DHAN_MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
DHAN_SOURCE_SEMANTICS = "dhan-raw-ohlcv-v1"
DHAN_IDENTITY_POLICY_VERSION = "shadow-identity-v1"
DHAN_CORPORATE_ACTION_POLICY_VERSION = "unresolved-v1"


class DhanDataError(RuntimeError):
    """Credential-safe Dhan market-data failure with operational metadata."""

    def __init__(
        self,
        message: str,
        *,
        http_status: int | None = None,
        error_code: str | None = None,
        retry_after: str | None = None,
    ) -> None:
        super().__init__(message)
        self.http_status = http_status
        self.error_code = error_code
        self.retry_after = retry_after


@dataclass(frozen=True)
class DhanInstrument:
    exchange: str
    security_id: str
    symbol: str
    isin: str
    series: str
    category: str
    display_name: str

    @property
    def instrument_id(self) -> str:
        return f"{self.exchange}:{self.security_id}"


@dataclass(frozen=True)
class DhanLiveQuote:
    """An observed Dhan LTP; it is never persisted as historical OHLCV."""

    price: float
    as_of: str


@dataclass(frozen=True)
class DhanMarketQuote:
    """Read-only Dhan market quote with exchange-provided change data."""

    price: float
    net_change: float
    previous_close: float | None
    as_of: str


class DhanMarketDataProvider(BaseMarketDataProvider):
    """Dhan historical-chart client; it contains no trading API operations."""

    provider_name = "dhan"
    source_semantics_version = DHAN_SOURCE_SEMANTICS

    def __init__(
        self,
        *,
        access_token: str | None = None,
        client_id: str | None = None,
        session: requests.Session | None = None,
        requests_per_second: float = 4.0,
    ) -> None:
        self._token = access_token or os.getenv("DHAN_ACCESS_TOKEN")
        self._client_id = client_id or os.getenv("DHAN_CLIENT_ID")
        self._session = session or requests.Session()
        # Explicit constructor credentials are used by deterministic tests.  The
        # production path validates credentials through the shared service.
        self._authentication = DhanAuthenticationService(session=self._session)
        self._auth_preflight_required = access_token is None and client_id is None
        self._interval = 1.0 / max(requests_per_second, 0.1)
        self._rate_lock = Lock()
        self._last_request = 0.0
        # Dhan's Market Quote endpoint has a stricter one-request-per-second
        # allowance than the historical endpoints used by this adapter.
        self._quote_rate_lock = Lock()
        self._last_quote_request = 0.0
        self._master: tuple[DhanInstrument, ...] | None = None

    def _throttle(self) -> None:
        with self._rate_lock:
            delay = self._interval - (monotonic() - self._last_request)
            if delay > 0:
                sleep(delay)
            self._last_request = monotonic()

    def _throttle_quote(self) -> None:
        with self._quote_rate_lock:
            delay = 1.0 - (monotonic() - self._last_quote_request)
            if delay > 0:
                sleep(delay)
            self._last_quote_request = monotonic()

    @property
    def _headers(self) -> dict[str, str]:
        # Never log or persist this mapping.
        headers = {
            "access-token": self._token or "",
            "Content-Type": "application/json",
        }
        if self._client_id:
            headers["client-id"] = self._client_id
        return headers

    def _ensure_client_id(self) -> None:
        """Resolve the Dhan client identity safely when only a token is configured."""
        if self._client_id:
            return
        self._ensure_authenticated()

    def _ensure_authenticated(self) -> None:
        """Use the one central authentication service; never expose credentials."""
        if not self._auth_preflight_required:
            return
        try:
            result = self._authentication.ensure_authenticated()
        except DhanAuthenticationError as error:
            raise DhanDataError(
                "Dhan authentication required.",
                http_status=401,
            ) from error
        self._token = result.access_token
        self._client_id = result.client_id

    def _recover_authenticated(self) -> None:
        """Regenerate once after an HTTP 401; caller owns the one retry limit."""
        try:
            result = self._authentication.recover_after_unauthorized()
        except DhanAuthenticationError as error:
            raise DhanDataError(
                "Dhan authentication required.",
                http_status=401,
            ) from error
        self._token = result.access_token
        self._client_id = result.client_id

    def _post(self, path: str, payload: dict[str, object]) -> dict[str, object]:
        self._ensure_authenticated()
        last_error: Exception | None = None
        authenticated_retry = False
        for attempt in range(4):
            self._throttle()
            response = self._session.post(
                f"{DHAN_API_ROOT}/{path.lstrip('/')}",
                headers=self._headers,
                json=payload,
                timeout=30,
            )
            if response.status_code == 401 and not authenticated_retry:
                authenticated_retry = True
                self._recover_authenticated()
                continue
            if response.status_code == 429 or response.status_code >= 500:
                retry_after = response.headers.get("Retry-After")
                last_error = DhanDataError(
                    f"Dhan HTTP {response.status_code}",
                    http_status=response.status_code,
                    retry_after=retry_after,
                )
                try:
                    provider_delay = float(retry_after or 0)
                except ValueError:
                    provider_delay = 0.0
                sleep(max(provider_delay, 0.5 * (2**attempt)))
                continue
            try:
                body = response.json()
            except ValueError:
                body = {}
            if response.status_code >= 400:
                raise DhanDataError(
                    f"Dhan HTTP {response.status_code}: "
                    f"{body.get('errorMessage', 'market data unavailable')}",
                    http_status=response.status_code,
                    error_code=(
                        str(body.get("errorCode"))
                        if body.get("errorCode") is not None
                        else None
                    ),
                    retry_after=response.headers.get("Retry-After"),
                )
            if isinstance(body, dict) and body.get("errorCode"):
                raise DhanDataError(
                    "Dhan data error "
                    f"{body.get('errorCode')}: "
                    f"{body.get('errorMessage', 'unknown')}",
                    http_status=response.status_code,
                    error_code=str(body.get("errorCode")),
                )
            return body
        raise last_error or RuntimeError("Dhan request failed after retries.")

    @staticmethod
    def source_fingerprint(
        instrument: DhanInstrument,
        *,
        timeframe: str,
        retrieval_revision: str,
    ) -> str:
        """Identify source semantics without claiming Yahoo equivalence."""

        identity = {
            "provider": "dhan",
            "api_version": "v2",
            "adjustment_semantics": "undocumented-observed-raw",
            "exchange": instrument.exchange,
            "security_id": instrument.security_id,
            "source_timeframe": timeframe,
            "retrieval_revision": retrieval_revision,
            "identity_policy": DHAN_IDENTITY_POLICY_VERSION,
            "corporate_action_policy": DHAN_CORPORATE_ACTION_POLICY_VERSION,
        }
        return hashlib.sha256(
            json.dumps(identity, sort_keys=True).encode("utf-8")
        ).hexdigest()

    def instrument_master(self, *, refresh: bool = False) -> tuple[DhanInstrument, ...]:
        if self._master is not None and not refresh:
            return self._master
        raw = pd.read_csv(DHAN_MASTER_URL, dtype=str).fillna("")
        eligible = raw[
            (raw["SEGMENT"] == "E")
            & (raw["INSTRUMENT"] == "EQUITY")
            & (raw["INSTRUMENT_TYPE"] == "ES")
            & raw["ISIN"].str.startswith("INE")
            & raw["EXCH_ID"].isin(["NSE", "BSE"])
        ]
        instruments: list[DhanInstrument] = []
        for row in eligible.to_dict("records"):
            exchange, series = row["EXCH_ID"], row["SERIES"]
            if exchange == "NSE":
                category = "NSE_MAIN" if series in {"EQ", "BE", "BZ"} else "NSE_SME"
            else:
                category = "BSE_SME" if series in {"M", "MT", "MS"} else "BSE_MAIN"
            instruments.append(
                DhanInstrument(
                    exchange=exchange,
                    security_id=row["SECURITY_ID"],
                    symbol=(
                        row.get("UNDERLYING_SYMBOL", "").strip()
                        or row["SYMBOL_NAME"].strip()
                    ).upper(),
                    isin=row["ISIN"],
                    series=series,
                    category=category,
                    display_name=row.get("DISPLAY_NAME", ""),
                )
            )
        self._master = tuple(instruments)
        return self._master

    def resolve(self, symbol: str, exchange: str = "NSE") -> DhanInstrument:
        normalized = symbol.strip().upper()
        matches = [
            item
            for item in self.instrument_master()
            if item.exchange == exchange and item.symbol == normalized
        ]
        if not matches:
            raise KeyError(f"No Dhan {exchange} equity mapping for {normalized}.")
        return sorted(
            matches, key=lambda item: (item.series != "EQ", item.security_id)
        )[0]

    def latest_quotes(
        self, instruments: list[DhanInstrument] | tuple[DhanInstrument, ...]
    ) -> dict[str, DhanLiveQuote]:
        """Fetch LTPs by exact Dhan exchange/security identity only."""
        self._ensure_client_id()
        grouped: dict[str, list[int]] = {}
        identities: dict[tuple[str, str], str] = {}
        for instrument in instruments:
            segment = f"{instrument.exchange}_EQ"
            security_id = str(instrument.security_id)
            try:
                grouped.setdefault(segment, []).append(int(security_id))
            except ValueError:
                # A malformed master record cannot be quoted; the response
                # layer will explicitly fall back to its persisted Dhan close.
                continue
            identities[(segment, security_id)] = instrument.instrument_id
        if not grouped:
            return {}
        observed_at = datetime.now(UTC).isoformat()
        quotes: dict[str, DhanLiveQuote] = {}
        # The Dhan endpoint accepts multiple exchange-segment lists per call.
        # Keep each request at its documented 1,000-instrument maximum.
        batches: list[dict[str, list[int]]] = []
        batch: dict[str, list[int]] = {}
        batch_size = 0
        for segment, security_ids in grouped.items():
            for security_id in security_ids:
                if batch_size == 1000:
                    batches.append(batch)
                    batch, batch_size = {}, 0
                batch.setdefault(segment, []).append(security_id)
                batch_size += 1
        if batch:
            batches.append(batch)
        for request in batches:
            self._throttle_quote()
            body = self._post("marketfeed/ltp", request)
            data = body.get("data", {})
            if not isinstance(data, dict):
                continue
            for segment, values in data.items():
                if not isinstance(values, dict):
                    continue
                for security_id, quote in values.items():
                    identity = identities.get((str(segment), str(security_id)))
                    price = quote.get("last_price") if isinstance(quote, dict) else None
                    try:
                        numeric_price = float(price)
                    except (TypeError, ValueError):
                        continue
                    if identity is not None and numeric_price > 0:
                        quotes[identity] = DhanLiveQuote(numeric_price, observed_at)
        return quotes

    def latest_market_quotes(
        self, instruments: dict[str, tuple[str, str]]
    ) -> dict[str, DhanMarketQuote]:
        """Fetch market quotes by the caller's exact Dhan segment and ID.

        This supports non-equity identities such as ``IDX_I`` and intentionally
        remains separate from :meth:`latest_quotes`, which uses the equity
        instrument master.
        """
        self._ensure_client_id()
        grouped: dict[str, list[int]] = {}
        identities: dict[tuple[str, str], str] = {}
        for identity, (segment, security_id) in instruments.items():
            try:
                numeric_id = int(security_id)
            except (TypeError, ValueError):
                continue
            grouped.setdefault(segment, []).append(numeric_id)
            identities[(segment, str(numeric_id))] = identity
        if not grouped:
            return {}
        self._throttle_quote()
        body = self._post("marketfeed/quote", grouped)
        data = body.get("data", {})
        if not isinstance(data, dict):
            return {}
        observed_at = datetime.now(UTC).isoformat()
        quotes: dict[str, DhanMarketQuote] = {}
        for segment, values in data.items():
            if not isinstance(values, dict):
                continue
            for security_id, quote in values.items():
                identity = identities.get((str(segment), str(security_id)))
                if identity is None or not isinstance(quote, dict):
                    continue
                try:
                    price = float(quote.get("last_price"))
                    net_change = float(quote.get("net_change", 0.0))
                except (TypeError, ValueError):
                    continue
                if price <= 0:
                    continue
                previous_close = price - net_change
                quotes[identity] = DhanMarketQuote(
                    price=price,
                    net_change=net_change,
                    previous_close=(previous_close if previous_close > 0 else None),
                    as_of=observed_at,
                )
        return quotes

    @staticmethod
    def _frame(body: dict[str, object]) -> DataFrame:
        timestamps = body.get("timestamp", [])
        frame = DataFrame(
            {
                "Open": body.get("open", []),
                "High": body.get("high", []),
                "Low": body.get("low", []),
                "Close": body.get("close", []),
                "Volume": body.get("volume", []),
            },
            index=pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(
                "Asia/Kolkata"
            ),
        )
        frame.index.name = None
        return (
            frame.apply(pd.to_numeric, errors="coerce")
            .dropna(subset=["Open", "High", "Low", "Close"])
            .sort_index()
        )

    def download_instrument_data(
        self,
        instrument: DhanInstrument,
        *,
        start: date,
        end: date,
        interval: str = "1d",
    ) -> DataFrame:
        common: dict[str, object] = {
            "securityId": instrument.security_id,
            "exchangeSegment": f"{instrument.exchange}_EQ",
            "instrument": "EQUITY",
            "fromDate": start.isoformat(),
            # Dhan documents Daily ``toDate`` as non-inclusive.  AlphaEdge's
            # provider contract is inclusive, so request the following date
            # and let the caller retain only completed exchange sessions.
            "toDate": (
                end + timedelta(days=1) if interval == "1d" else end
            ).isoformat(),
        }
        if interval == "1d":
            return self._frame(self._post("charts/historical", common))
        minutes = {"1m": 1, "5m": 5, "15m": 15, "60m": 60}.get(interval)
        if minutes is None:
            raise ValueError(f"Dhan does not directly support interval {interval}.")
        common["interval"] = str(minutes)
        return self._frame(self._post("charts/intraday", common))

    @staticmethod
    def _period_start(period: str, end: date) -> date:
        days = {
            "1mo": 31,
            "3mo": 93,
            "6mo": 186,
            "1y": 366,
            "2y": 732,
            "5y": 1830,
            "10y": 3660,
        }
        return end - timedelta(days=days.get(period, 366))

    def download_stock_data(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> DataFrame:
        end = datetime.now().date()
        return self.download_instrument_data(
            self.resolve(symbol),
            start=self._period_start(period, end),
            end=end,
            interval=interval,
        )

    def download_stock_data_since(
        self, symbol: str, *, start: object, interval: str = "1d"
    ) -> DataFrame:
        stamp = pd.Timestamp(start)
        return self.download_instrument_data(
            self.resolve(symbol),
            start=stamp.date(),
            end=datetime.now().date(),
            interval=interval,
        )
