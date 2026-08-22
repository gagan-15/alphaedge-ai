"""
Tests for secure password hashing.
"""

import pytest

from backend.security.password_service import PasswordService


def test_password_is_hashed_and_verified() -> None:
    service = PasswordService()
    password = "StrongPassword!42"

    password_hash = service.hash_password(
        password,
    )

    assert password_hash != password
    assert service.verify_password(
        password,
        password_hash,
    )
    assert not service.verify_password(
        "WrongPassword!42",
        password_hash,
    )


@pytest.mark.parametrize(
    "password",
    [
        "Short!1",
        "alllowercase!42",
        "ALLUPPERCASE!42",
        "MissingNumber!",
        "MissingSpecial42",
    ],
)
def test_weak_password_is_rejected(
    password: str,
) -> None:
    service = PasswordService()

    with pytest.raises(
        ValueError,
    ):
        service.hash_password(
            password,
        )
