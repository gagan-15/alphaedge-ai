"""Central, credential-safe Dhan authentication for read-only market data.

Only Dhan's documented individual-user endpoints are used here:
``/v2/profile``, ``/v2/RenewToken`` and the TOTP-enabled
``/app/generateAccessToken`` endpoint.  This module has no trading actions.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock
from time import monotonic
from typing import Any, Callable
from zoneinfo import ZoneInfo

import pyotp
import requests
from dotenv import dotenv_values

DHAN_API_ROOT = "https://api.dhan.co/v2"
DHAN_AUTH_ROOT = "https://auth.dhan.co/app"
_AUTH_CACHE_SECONDS = 300.0
_RENEW_BEFORE = timedelta(minutes=30)
_DHAN_TIMEZONE = ZoneInfo("Asia/Kolkata")
_ENV_KEYS = (
    "DHAN_ACCESS_TOKEN",
    "DHAN_CLIENT_ID",
    "DHAN_PIN",
    "DHAN_TOTP_SECRET",
    "DHAN_ACCESS_TOKEN_EXPIRES_AT",
)


class DhanAuthenticationError(RuntimeError):
    """Sanitized authentication failure safe for operational logs and APIs."""

    def __init__(self, message: str = "Dhan authentication required.") -> None:
        super().__init__(message)


@dataclass(frozen=True)
class DhanAuthenticationResult:
    """In-process result.  Never serialize this object to an API response."""

    status: str
    access_token: str | None
    client_id: str | None
    expires_at: datetime | None


class DhanCredentialStore:
    """Read/write ignored local credentials without leaking their contents."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(__file__).resolve().parents[3] / ".env"

    def value(self, key: str) -> str | None:
        values = dotenv_values(self.path) if self.path.exists() else {}
        value = values.get(key) or os.getenv(key)
        return str(value).strip() if value else None

    def persist_access_token(self, token: str, expires_at: datetime | None) -> None:
        """Atomically persist only the renewed/generated token metadata locally."""
        if not token or not self.path.exists():
            raise DhanAuthenticationError("Dhan authentication required.")
        replacements = {
            "DHAN_ACCESS_TOKEN": token,
            "DHAN_ACCESS_TOKEN_EXPIRES_AT": (
                expires_at.astimezone(UTC).isoformat() if expires_at else ""
            ),
        }
        original = self.path.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        seen: set[str] = set()
        rewritten: list[str] = []
        for line in lines:
            match = re.match(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*)=", line)
            if match and match.group(2) in replacements:
                key = match.group(2)
                rewritten.append(
                    f"{match.group(1)}{key}{match.group(3)}={replacements[key]}\n"
                )
                seen.add(key)
            else:
                rewritten.append(line)
        if rewritten and not rewritten[-1].endswith(("\n", "\r")):
            rewritten[-1] += "\n"
        for key in replacements:
            if key not in seen:
                rewritten.append(f"{key}={replacements[key]}\n")
        with NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="",
            dir=self.path.parent,
            delete=False,
            prefix=".alphaedge-auth-",
        ) as temporary:
            temporary.writelines(rewritten)
            temporary_path = Path(temporary.name)
        try:
            os.replace(temporary_path, self.path)
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                pass
        finally:
            if temporary_path.exists():
                temporary_path.unlink(missing_ok=True)
        os.environ["DHAN_ACCESS_TOKEN"] = token
        if expires_at:
            os.environ["DHAN_ACCESS_TOKEN_EXPIRES_AT"] = expires_at.astimezone(
                UTC
            ).isoformat()


class DhanAuthenticationService:
    """One bounded authentication mechanism shared by every Dhan read path."""

    _status_lock = RLock()
    _last_status = "AUTH_REQUIRED"

    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        credentials: DhanCredentialStore | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._session = session or requests.Session()
        self._credentials = credentials or DhanCredentialStore()
        self._now = now or (lambda: datetime.now(UTC))
        self._cached: DhanAuthenticationResult | None = None
        self._cached_at = 0.0
        self._lock = RLock()

    @classmethod
    def last_known_status(cls) -> str:
        with cls._status_lock:
            return cls._last_status

    @classmethod
    def _set_status(cls, status: str) -> None:
        with cls._status_lock:
            cls._last_status = status

    @staticmethod
    def _parse_expiry(value: object) -> datetime | None:
        if not value:
            return None
        text = str(value).strip()
        for parser in (
            lambda: datetime.fromisoformat(text.replace("Z", "+00:00")),
            lambda: datetime.strptime(text, "%d/%m/%Y %H:%M"),
        ):
            try:
                parsed = parser()
                return (
                    parsed.replace(tzinfo=_DHAN_TIMEZONE).astimezone(UTC)
                    if parsed.tzinfo is None
                    else parsed.astimezone(UTC)
                )
            except ValueError:
                continue
        return None

    @staticmethod
    def _body(response: Any) -> dict[str, object]:
        try:
            body = response.json()
        except (ValueError, AttributeError):
            return {}
        return body if isinstance(body, dict) else {}

    def _profile(self, token: str) -> tuple[str | None, datetime | None, bool]:
        try:
            response = self._session.get(
                f"{DHAN_API_ROOT}/profile",
                headers={"access-token": token},
                timeout=30,
            )
        except requests.RequestException as error:
            raise DhanAuthenticationError(
                "Dhan authentication could not be verified."
            ) from error
        body = self._body(response)
        if response.status_code == 401:
            return None, None, False
        if response.status_code >= 400:
            raise DhanAuthenticationError("Dhan authentication could not be verified.")
        client_id = body.get("dhanClientId")
        return (
            str(client_id) if client_id else None,
            self._parse_expiry(body.get("tokenValidity")),
            bool(client_id),
        )

    def _persist_result(
        self,
        body: dict[str, object],
        status: str,
        *,
        fallback_client_id: str | None = None,
    ) -> DhanAuthenticationResult:
        token = body.get("accessToken")
        client_id = (
            body.get("dhanClientId")
            or fallback_client_id
            or self._credentials.value("DHAN_CLIENT_ID")
        )
        if not token or not client_id:
            raise DhanAuthenticationError("Dhan authentication required.")
        expires_at = self._parse_expiry(body.get("expiryTime"))
        self._credentials.persist_access_token(str(token), expires_at)
        result = DhanAuthenticationResult(
            status, str(token), str(client_id), expires_at
        )
        self._cached, self._cached_at = result, monotonic()
        self._set_status(status)
        return result

    def _renew(self, token: str, client_id: str) -> DhanAuthenticationResult | None:
        try:
            response = self._session.get(
                f"{DHAN_API_ROOT}/RenewToken",
                headers={"access-token": token, "dhanClientId": client_id},
                timeout=30,
            )
        except requests.RequestException:
            return None
        if response.status_code >= 400:
            return None
        return self._persist_result(
            self._body(response),
            "AUTH_RENEWED",
            fallback_client_id=client_id,
        )

    def _regenerate(self) -> DhanAuthenticationResult:
        client_id = self._credentials.value("DHAN_CLIENT_ID")
        pin = self._credentials.value("DHAN_PIN")
        secret = self._credentials.value("DHAN_TOTP_SECRET")
        if not client_id or not pin or not secret:
            self._set_status("AUTH_REQUIRED")
            raise DhanAuthenticationError("Dhan authentication required.")
        try:
            totp = pyotp.TOTP(secret).now()
            response = self._session.post(
                f"{DHAN_AUTH_ROOT}/generateAccessToken",
                params={"dhanClientId": client_id, "pin": pin, "totp": totp},
                timeout=30,
            )
        except (requests.RequestException, ValueError) as error:
            self._set_status("AUTH_REQUIRED")
            raise DhanAuthenticationError("Dhan authentication required.") from error
        if response.status_code >= 400:
            self._set_status("AUTH_REQUIRED")
            raise DhanAuthenticationError("Dhan authentication required.")
        return self._persist_result(self._body(response), "AUTH_REGENERATED")

    def ensure_authenticated(self, *, force: bool = False) -> DhanAuthenticationResult:
        """Validate an active token and renew only inside the official safe window."""
        with self._lock:
            if (
                not force
                and self._cached is not None
                and monotonic() - self._cached_at < _AUTH_CACHE_SECONDS
            ):
                return self._cached
            token = self._credentials.value("DHAN_ACCESS_TOKEN")
            if token:
                client_id, profile_expiry, valid = self._profile(token)
                if valid and client_id:
                    configured_client_id = self._credentials.value("DHAN_CLIENT_ID")
                    if configured_client_id and configured_client_id != client_id:
                        self._set_status("AUTH_REQUIRED")
                        raise DhanAuthenticationError("Dhan authentication required.")
                    expiry = profile_expiry or self._parse_expiry(
                        self._credentials.value("DHAN_ACCESS_TOKEN_EXPIRES_AT")
                    )
                    if expiry and self._now() >= expiry - _RENEW_BEFORE:
                        renewed = self._renew(token, client_id)
                        if renewed is not None:
                            return renewed
                    result = DhanAuthenticationResult(
                        "AUTH_VALID", token, client_id, expiry
                    )
                    self._cached, self._cached_at = result, monotonic()
                    self._set_status(result.status)
                    return result
            return self._regenerate()

    def recover_after_unauthorized(self) -> DhanAuthenticationResult:
        """One explicit recovery attempt after a Dhan operation returns HTTP 401."""
        with self._lock:
            self._cached = None
            return self._regenerate()
