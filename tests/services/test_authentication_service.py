"""
Tests for multi-device authentication sessions.
"""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.api.models.auth_request import RegistrationRequest
from backend.config.auth_config import AuthConfig
from backend.database.base import Base
from backend.models.auth.auth_session import AuthSession
from backend.security.token_service import TokenService
from backend.services.auth.authentication_service import AuthenticationService
from backend.services.auth.registration_service import RegistrationService


def build_session() -> Session:
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

    return Session(
        engine,
        expire_on_commit=False,
    )


def build_config() -> AuthConfig:
    return AuthConfig(
        secret_key="a-secure-test-secret-with-more-than-32-characters",
    )


def create_verified_user(
    session: Session,
) -> None:
    user = RegistrationService().register(
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
    user.is_email_verified = True
    session.commit()


def test_multiple_devices_create_separate_sessions() -> None:
    with build_session() as session:
        create_verified_user(
            session,
        )
        service = AuthenticationService(
            build_config(),
        )

        service.login(
            email="gagan@example.com",
            password="StrongPassword!42",
            device_name="Laptop",
            session=session,
        )
        service.login(
            email="gagan@example.com",
            password="StrongPassword!42",
            device_name="Phone",
            session=session,
        )
        sessions = session.scalars(
            select(AuthSession),
        ).all()

        assert len(sessions) == 2
        assert {auth_session.device_name for auth_session in sessions} == {
            "Laptop",
            "Phone",
        }


def test_refresh_rotates_and_revokes_old_session() -> None:
    with build_session() as session:
        create_verified_user(
            session,
        )
        service = AuthenticationService(
            build_config(),
        )
        login_result = service.login(
            email="gagan@example.com",
            password="StrongPassword!42",
            device_name="Laptop",
            session=session,
        )

        refresh_result = service.refresh(
            refresh_token=login_result.refresh_token,
            session=session,
        )
        sessions = session.scalars(
            select(AuthSession).order_by(
                AuthSession.created_at,
            ),
        ).all()

        assert len(sessions) == 2
        assert sessions[0].revoked_at is not None
        assert sessions[1].revoked_at is None
        assert refresh_result.refresh_token != login_result.refresh_token


def test_logout_all_revokes_every_device() -> None:
    with build_session() as session:
        create_verified_user(
            session,
        )
        service = AuthenticationService(
            build_config(),
        )
        laptop = service.login(
            email="gagan@example.com",
            password="StrongPassword!42",
            device_name="Laptop",
            session=session,
        )
        service.login(
            email="gagan@example.com",
            password="StrongPassword!42",
            device_name="Phone",
            session=session,
        )

        service.logout_all(
            refresh_token=laptop.refresh_token,
            session=session,
        )
        sessions = session.scalars(
            select(AuthSession),
        ).all()

        assert all(auth_session.revoked_at is not None for auth_session in sessions)


def test_unverified_user_cannot_login() -> None:
    with build_session() as session:
        user = RegistrationService().register(
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
        assert user.is_email_verified is False

        service = AuthenticationService(
            build_config(),
        )

        try:
            service.login(
                email="gagan@example.com",
                password="StrongPassword!42",
                device_name="Laptop",
                session=session,
            )
        except ValueError as error:
            assert str(error) == "Email verification is required."
        else:
            raise AssertionError("Unverified user was allowed to login.")


def test_access_token_is_short_lived_access_type() -> None:
    with build_session() as session:
        create_verified_user(
            session,
        )
        config = build_config()
        result = AuthenticationService(
            config,
        ).login(
            email="gagan@example.com",
            password="StrongPassword!42",
            device_name="Laptop",
            session=session,
        )
        payload = TokenService(
            config,
        ).decode_token(
            result.access_token,
            expected_type="access",
        )

        assert payload["type"] == "access"
