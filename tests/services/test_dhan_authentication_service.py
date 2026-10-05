from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from backend.services.market_data.dhan_authentication_service import (
    DhanAuthenticationError,
    DhanAuthenticationService,
    DhanCredentialStore,
)
from backend.data_providers.dhan.dhan_provider import DhanMarketDataProvider


class _Response:
    headers: dict[str, str] = {}

    def __init__(self, status_code: int, body: dict[str, object]) -> None:
        self.status_code = status_code
        self._body = body

    def json(self) -> dict[str, object]:
        return self._body


class _Session:
    def __init__(self, gets: list[_Response], posts: list[_Response]) -> None:
        self.gets = gets
        self.posts = posts
        self.get_calls: list[tuple[str, dict[str, str]]] = []
        self.post_calls: list[tuple[str, dict[str, object]]] = []

    def get(self, url: str, *, headers: dict[str, str], timeout: int) -> _Response:
        del timeout
        self.get_calls.append((url, headers))
        return self.gets.pop(0)

    def post(self, url: str, *, params: dict[str, object], timeout: int) -> _Response:
        del timeout
        self.post_calls.append((url, params))
        return self.posts.pop(0)


def _credentials(tmp_path: Path, text: str) -> DhanCredentialStore:
    path = tmp_path / ".env"
    path.write_text(text, encoding="utf-8")
    return DhanCredentialStore(path)


def test_active_token_is_validated_without_renewal(tmp_path: Path) -> None:
    session = _Session(
        [
            _Response(
                200, {"dhanClientId": "client", "tokenValidity": "31/08/2026 18:00"}
            )
        ],
        [],
    )
    service = DhanAuthenticationService(
        session=session,
        credentials=_credentials(tmp_path, "DHAN_ACCESS_TOKEN=active\n"),
        now=lambda: datetime(2026, 8, 30, 9, tzinfo=UTC),
    )

    result = service.ensure_authenticated()

    assert result.status == "AUTH_VALID"
    assert result.client_id == "client"
    assert session.post_calls == []


def test_near_expiry_active_token_uses_official_renew_endpoint(tmp_path: Path) -> None:
    session = _Session(
        [
            _Response(
                200, {"dhanClientId": "client", "tokenValidity": "30/08/2026 15:20"}
            ),
            _Response(
                200, {"accessToken": "renewed", "expiryTime": "31/08/2026 15:20"}
            ),
        ],
        [],
    )
    service = DhanAuthenticationService(
        session=session,
        credentials=_credentials(tmp_path, "DHAN_ACCESS_TOKEN=active\n"),
        now=lambda: datetime(2026, 8, 30, 9, 40, tzinfo=UTC),
    )

    result = service.ensure_authenticated()

    assert result.status == "AUTH_RENEWED"
    assert result.access_token == "renewed"
    assert session.get_calls[1][0].endswith("/RenewToken")
    assert session.get_calls[1][1]["dhanClientId"] == "client"
    assert "DHAN_ACCESS_TOKEN=renewed" in (tmp_path / ".env").read_text(
        encoding="utf-8"
    )


def test_invalid_token_regenerates_from_locally_generated_totp(tmp_path: Path) -> None:
    session = _Session(
        [_Response(401, {})],
        [
            _Response(
                200,
                {
                    "accessToken": "fresh",
                    "dhanClientId": "client",
                    "expiryTime": "2026-08-31T15:20:00",
                },
            )
        ],
    )
    credentials = _credentials(
        tmp_path,
        (
            "DHAN_ACCESS_TOKEN=expired\nDHAN_CLIENT_ID=client\n"
            "DHAN_PIN=123456\nDHAN_TOTP_SECRET=JBSWY3DPEHPK3PXP\n"
        ),
    )
    result = DhanAuthenticationService(
        session=session, credentials=credentials
    ).ensure_authenticated()

    assert result.status == "AUTH_REGENERATED"
    assert result.access_token == "fresh"
    assert session.post_calls[0][0].endswith("/generateAccessToken")
    assert set(session.post_calls[0][1]) == {"dhanClientId", "pin", "totp"}
    assert "DHAN_ACCESS_TOKEN=fresh" in (tmp_path / ".env").read_text(encoding="utf-8")


def test_invalid_token_without_totp_configuration_fails_closed(tmp_path: Path) -> None:
    session = _Session([_Response(401, {})], [])
    service = DhanAuthenticationService(
        session=session,
        credentials=_credentials(tmp_path, "DHAN_ACCESS_TOKEN=expired\n"),
    )

    with pytest.raises(DhanAuthenticationError, match="Dhan authentication required"):
        service.ensure_authenticated()
    assert session.post_calls == []


def test_provider_retries_an_unauthorized_read_once_after_central_recovery() -> None:
    class _ProviderSession:
        def __init__(self) -> None:
            self.calls = 0

        def post(
            self,
            url: str,
            *,
            headers: dict[str, str],
            json: dict[str, object],
            timeout: int,
        ) -> _Response:
            del url, headers, json, timeout
            self.calls += 1
            return (
                _Response(401, {}) if self.calls == 1 else _Response(200, {"ok": True})
            )

    class _Recovery:
        calls = 0

        def recover_after_unauthorized(self):
            self.calls += 1
            return type(
                "Recovered", (), {"access_token": "fresh", "client_id": "client"}
            )()

    session = _ProviderSession()
    provider = DhanMarketDataProvider(
        access_token="expired",
        client_id="client",
        session=session,  # type: ignore[arg-type]
    )
    recovery = _Recovery()
    provider._authentication = recovery  # type: ignore[assignment]

    assert provider._post("marketfeed/ltp", {"NSE_EQ": [1]}) == {"ok": True}
    assert recovery.calls == 1
    assert session.calls == 2
