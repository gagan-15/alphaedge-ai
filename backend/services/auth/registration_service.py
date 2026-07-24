"""
User registration service.
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.api.models.auth_request import RegistrationRequest
from backend.models.auth.user import User
from backend.security.password_service import PasswordService


class RegistrationService:
    """
    Validate consent and create a new inactive-email account.
    """

    def __init__(
        self,
        password_service: PasswordService | None = None,
    ) -> None:
        self._password_service = password_service or PasswordService()

    def register(
        self,
        request: RegistrationRequest,
        session: Session,
    ) -> User:
        """
        Create a user after all required safety consent is accepted.
        """

        self._validate_consent(
            request,
        )
        normalized_email = (
            str(
                request.email,
            )
            .strip()
            .lower()
        )
        existing_user = session.scalar(
            select(User).where(
                User.email == normalized_email,
            )
        )

        if existing_user is not None:
            raise ValueError(
                "An account with this email already exists.",
            )

        accepted_at = datetime.now(UTC)
        user = User(
            full_name=request.full_name,
            email=normalized_email,
            country=request.country,
            password_hash=self._password_service.hash_password(
                request.password,
            ),
            is_adult_confirmed=True,
            terms_accepted_at=accepted_at,
            risk_disclosure_accepted_at=accepted_at,
        )
        session.add(
            user,
        )

        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise ValueError(
                "An account with this email already exists.",
            ) from error

        session.refresh(
            user,
        )

        return user

    @staticmethod
    def _validate_consent(
        request: RegistrationRequest,
    ) -> None:
        if not request.accepts_terms:
            raise ValueError(
                "Terms must be accepted.",
            )

        if not request.accepts_risk_disclosure:
            raise ValueError(
                "Risk disclosure must be accepted.",
            )

        if not request.confirms_adult:
            raise ValueError(
                "Registration is available only to adults.",
            )
