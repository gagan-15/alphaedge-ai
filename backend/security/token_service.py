"""
Signed authentication token service.
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from backend.config.auth_config import AuthConfig


class TokenService:
    """
    Create and validate short access and rotating refresh tokens.
    """

    def __init__(
        self,
        config: AuthConfig,
    ) -> None:
        config.validate()
        self._config = config

    def create_access_token(
        self,
        user_id: str,
    ) -> str:
        """
        Create a short-lived access token.
        """

        return self._create_token(
            user_id=user_id,
            token_type="access",
            expires_delta=timedelta(
                minutes=self._config.access_token_minutes,
            ),
        )

    def create_refresh_token(
        self,
        user_id: str,
    ) -> str:
        """
        Create a refresh token with a unique rotation identifier.
        """

        return self._create_token(
            user_id=user_id,
            token_type="refresh",
            expires_delta=timedelta(
                days=self._config.refresh_token_days,
            ),
        )

    def decode_token(
        self,
        token: str,
        expected_type: str,
    ) -> dict[str, object]:
        """
        Validate a token and its expected use.
        """

        payload = jwt.decode(
            token,
            self._config.secret_key,
            algorithms=[
                self._config.algorithm,
            ],
        )

        if payload.get("type") != expected_type:
            raise ValueError(
                "Token type is invalid.",
            )

        return payload

    def _create_token(
        self,
        user_id: str,
        token_type: str,
        expires_delta: timedelta,
    ) -> str:
        if not user_id:
            raise ValueError(
                "user_id cannot be empty.",
            )

        issued_at = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "type": token_type,
            "jti": str(uuid4()),
            "iat": issued_at,
            "exp": issued_at + expires_delta,
        }

        return jwt.encode(
            payload,
            self._config.secret_key,
            algorithm=self._config.algorithm,
        )
