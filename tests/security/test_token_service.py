"""
Tests for signed authentication tokens.
"""

import pytest

from backend.config.auth_config import AuthConfig
from backend.security.token_service import TokenService


def build_service() -> TokenService:
    return TokenService(
        AuthConfig(
            secret_key="a-secure-test-secret-with-more-than-32-characters",
        )
    )


def test_access_token_contains_user_and_type() -> None:
    service = build_service()

    token = service.create_access_token(
        "user-123",
    )
    payload = service.decode_token(
        token,
        expected_type="access",
    )

    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert payload["jti"]


def test_refresh_token_cannot_be_used_as_access_token() -> None:
    service = build_service()
    token = service.create_refresh_token(
        "user-123",
    )

    with pytest.raises(
        ValueError,
        match="Token type is invalid",
    ):
        service.decode_token(
            token,
            expected_type="access",
        )


def test_weak_secret_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="at least 32 characters",
    ):
        TokenService(
            AuthConfig(
                secret_key="weak",
            )
        )
