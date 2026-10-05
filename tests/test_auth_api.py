"""
Tests for the registration API response.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.api.auth import register
from backend.api.models.auth_request import RegistrationRequest
from backend.database.base import Base


def test_register_returns_safe_public_user() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
    )

    with Session(
        engine,
        expire_on_commit=False,
    ) as session:
        response = register(
            request=RegistrationRequest(
                full_name="Gagan Devali",
                email="gagan@example.com",
                password="StrongPassword!42",
                country="IN",
                accepts_terms=True,
                accepts_risk_disclosure=True,
                confirms_adult=True,
            ),
            session=session,
        )

    assert response.user.email == "gagan@example.com"
    assert response.user.is_email_verified is False
    assert "password" not in response.model_dump()
