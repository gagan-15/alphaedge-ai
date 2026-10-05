"""
Tests for safe user registration.
"""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.api.models.auth_request import RegistrationRequest
from backend.database.base import Base
from backend.models.auth.user import User
from backend.services.auth.registration_service import RegistrationService


@pytest.fixture
def session() -> Session:
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
    ) as database_session:
        yield database_session


def build_request(
    **overrides: object,
) -> RegistrationRequest:
    values: dict[str, object] = {
        "full_name": "Gagan Devali",
        "email": "gagan@example.com",
        "password": "StrongPassword!42",
        "country": "in",
        "accepts_terms": True,
        "accepts_risk_disclosure": True,
        "confirms_adult": True,
    }
    values.update(
        overrides,
    )

    return RegistrationRequest.model_validate(
        values,
    )


def test_registration_stores_minimum_safe_user_data(
    session: Session,
) -> None:
    service = RegistrationService()

    user = service.register(
        request=build_request(),
        session=session,
    )
    stored_user = session.scalar(
        select(User).where(
            User.email == "gagan@example.com",
        )
    )

    assert stored_user is not None
    assert user.id == stored_user.id
    assert user.country == "IN"
    assert user.password_hash != "StrongPassword!42"
    assert user.is_adult_confirmed is True
    assert user.is_email_verified is False
    assert user.terms_accepted_at is not None
    assert user.risk_disclosure_accepted_at is not None


def test_duplicate_email_is_rejected(
    session: Session,
) -> None:
    service = RegistrationService()
    request = build_request()
    service.register(
        request=request,
        session=session,
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        service.register(
            request=request,
            session=session,
        )


@pytest.mark.parametrize(
    (
        "field",
        "message",
    ),
    [
        (
            "accepts_terms",
            "Terms must be accepted",
        ),
        (
            "accepts_risk_disclosure",
            "Risk disclosure must be accepted",
        ),
        (
            "confirms_adult",
            "only to adults",
        ),
    ],
)
def test_required_consent_is_enforced(
    session: Session,
    field: str,
    message: str,
) -> None:
    service = RegistrationService()

    with pytest.raises(
        ValueError,
        match=message,
    ):
        service.register(
            request=build_request(
                **{
                    field: False,
                }
            ),
            session=session,
        )
