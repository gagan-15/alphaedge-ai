"""
Login and revocable multi-device session service.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.config.auth_config import AuthConfig
from backend.models.auth.auth_session import AuthSession
from backend.models.auth.user import User
from backend.security.password_service import PasswordService
from backend.security.token_service import TokenService


@dataclass(frozen=True)
class AuthenticationResult:
    """
    Tokens and user produced by successful authentication.
    """

    access_token: str
    refresh_token: str
    user: User


class AuthenticationService:
    """
    Manage login, rotation, and session revocation.
    """

    def __init__(
        self,
        config: AuthConfig,
        password_service: PasswordService | None = None,
    ) -> None:
        config.validate()
        self._config = config
        self._password_service = password_service or PasswordService()
        self._token_service = TokenService(
            config,
        )

    def login(
        self,
        email: str,
        password: str,
        device_name: str | None,
        session: Session,
    ) -> AuthenticationResult:
        """
        Verify credentials and create one device session.
        """

        normalized_email = email.strip().lower()
        user = session.scalar(
            select(User).where(
                User.email == normalized_email,
            )
        )

        if user is None or not self._password_service.verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError(
                "Email or password is incorrect.",
            )

        if not user.is_active:
            raise ValueError(
                "Account is inactive.",
            )

        if not user.is_email_verified:
            raise ValueError(
                "Email verification is required.",
            )

        return self._create_session(
            user=user,
            device_name=device_name,
            session=session,
        )

    def refresh(
        self,
        refresh_token: str,
        session: Session,
    ) -> AuthenticationResult:
        """
        Rotate a valid refresh token and revoke its old session.
        """

        payload = self._token_service.decode_token(
            refresh_token,
            expected_type="refresh",
        )
        token_jti = str(
            payload["jti"],
        )
        auth_session = session.scalar(
            select(AuthSession).where(
                AuthSession.refresh_token_jti == token_jti,
            )
        )
        now = datetime.now(UTC)

        if (
            auth_session is None
            or auth_session.revoked_at is not None
            or self._as_utc(auth_session.expires_at) <= now
        ):
            raise ValueError(
                "Session is invalid or expired.",
            )

        user = session.get(
            User,
            UUID(
                str(payload["sub"]),
            ),
        )

        if user is None or not user.is_active:
            raise ValueError(
                "Account is unavailable.",
            )

        auth_session.revoked_at = now
        auth_session.last_used_at = now

        return self._create_session(
            user=user,
            device_name=auth_session.device_name,
            session=session,
        )

    def logout(
        self,
        refresh_token: str,
        session: Session,
    ) -> None:
        """
        Revoke the current device session.
        """

        payload = self._token_service.decode_token(
            refresh_token,
            expected_type="refresh",
        )
        auth_session = session.scalar(
            select(AuthSession).where(
                AuthSession.refresh_token_jti == str(payload["jti"]),
            )
        )

        if auth_session is not None and auth_session.revoked_at is None:
            auth_session.revoked_at = datetime.now(UTC)
            session.commit()

    def logout_all(
        self,
        refresh_token: str,
        session: Session,
    ) -> None:
        """
        Revoke every active session belonging to the user.
        """

        payload = self._token_service.decode_token(
            refresh_token,
            expected_type="refresh",
        )
        session.execute(
            update(AuthSession)
            .where(
                AuthSession.user_id
                == UUID(
                    str(payload["sub"]),
                ),
                AuthSession.revoked_at.is_(None),
            )
            .values(
                revoked_at=datetime.now(UTC),
            )
        )
        session.commit()

    def _create_session(
        self,
        user: User,
        device_name: str | None,
        session: Session,
    ) -> AuthenticationResult:
        refresh_token = self._token_service.create_refresh_token(
            str(user.id),
        )
        refresh_payload = self._token_service.decode_token(
            refresh_token,
            expected_type="refresh",
        )
        auth_session = AuthSession(
            user_id=user.id,
            refresh_token_jti=str(
                refresh_payload["jti"],
            ),
            device_name=device_name,
            expires_at=datetime.now(UTC)
            + timedelta(
                days=self._config.refresh_token_days,
            ),
        )
        session.add(
            auth_session,
        )
        session.commit()

        return AuthenticationResult(
            access_token=self._token_service.create_access_token(
                str(user.id),
            ),
            refresh_token=refresh_token,
            user=user,
        )

    @staticmethod
    def _as_utc(
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None:
            return value.replace(
                tzinfo=UTC,
            )

        return value.astimezone(
            UTC,
        )
