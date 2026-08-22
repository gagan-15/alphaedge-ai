"""Tests for local email verification."""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.api.models.auth_request import RegistrationRequest
from backend.database.base import Base
from backend.models.auth.email_verification_token import EmailVerificationToken
from backend.services.auth.email_verification_service import (
    EmailVerificationService,
)
from backend.services.auth.registration_service import RegistrationService


def test_verification_token_is_hashed_one_time_and_marks_user_verified() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine, expire_on_commit=False) as session:
        user = RegistrationService().register(
            RegistrationRequest(
                full_name="Gagan Devali",
                email="gagan@example.com",
                password="StrongPassword!42",
                country="IN",
                accepts_terms=True,
                accepts_risk_disclosure=True,
                confirms_adult=True,
            ),
            session,
        )
        service = EmailVerificationService()
        raw_token = "a-valid-one-time-verification-token-123456"
        token = EmailVerificationToken(
            user_id=user.id,
            token_hash=service._hash_token(raw_token),
            expires_at=user.created_at.replace(year=user.created_at.year + 1),
        )
        session.add(token)
        session.commit()

        verified_user = service.verify(raw_token, session)

        assert verified_user.is_email_verified is True
        assert token.used_at is not None
        assert token.token_hash != raw_token

        try:
            service.verify(raw_token, session)
        except ValueError as error:
            assert "invalid or expired" in str(error)
        else:
            raise AssertionError("Used verification token was accepted.")


def test_unknown_email_does_not_create_token() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        EmailVerificationService().request_verification(
            "unknown@example.com",
            session,
        )

        assert session.scalar(select(EmailVerificationToken)) is None
