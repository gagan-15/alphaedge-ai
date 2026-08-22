"""Free local email verification service."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.core.logger import logger
from backend.models.auth.email_verification_token import EmailVerificationToken
from backend.models.auth.user import User


class EmailVerificationService:
    """Create and consume secure one-time email verification tokens."""

    def __init__(
        self,
        token_lifetime_hours: int = 24,
        frontend_url: str = "http://127.0.0.1:5173",
    ) -> None:
        if token_lifetime_hours <= 0:
            raise ValueError("token_lifetime_hours must be greater than zero.")

        self._token_lifetime_hours = token_lifetime_hours
        self._frontend_url = frontend_url.rstrip("/")

    def request_verification(
        self,
        email: str,
        session: Session,
    ) -> None:
        """Create a new token when an unverified account exists."""

        user = session.scalar(select(User).where(User.email == email.strip().lower()))

        if user is None or user.is_email_verified or not user.is_active:
            return

        session.execute(
            update(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.used_at.is_(None),
            )
            .values(used_at=datetime.now(UTC))
        )
        raw_token = secrets.token_urlsafe(32)
        session.add(
            EmailVerificationToken(
                user_id=user.id,
                token_hash=self._hash_token(raw_token),
                expires_at=datetime.now(UTC)
                + timedelta(hours=self._token_lifetime_hours),
            )
        )
        session.commit()
        logger.info(
            "Development email verification link for %s: %s/verify-email?token=%s",
            user.email,
            self._frontend_url,
            raw_token,
        )

    def verify(
        self,
        raw_token: str,
        session: Session,
    ) -> User:
        """Verify one valid token and mark the account email as verified."""

        token = session.scalar(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == self._hash_token(raw_token)
            )
        )
        now = datetime.now(UTC)

        if (
            token is None
            or token.used_at is not None
            or self._as_utc(token.expires_at) <= now
        ):
            raise ValueError("Verification link is invalid or expired.")

        user = session.get(User, token.user_id)

        if user is None or not user.is_active:
            raise ValueError("Account is unavailable.")

        user.is_email_verified = True
        token.used_at = now
        session.commit()

        return user

    @staticmethod
    def _hash_token(raw_token: str) -> str:
        if not raw_token:
            raise ValueError("Verification token is required.")

        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)

        return value.astimezone(UTC)
