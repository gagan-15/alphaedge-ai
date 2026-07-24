"""
Authentication API.
"""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.api.models.auth_request import (
    EmailVerificationRequest,
    LoginRequest,
    RegistrationRequest,
    VerifyEmailRequest,
)
from backend.api.models.auth_response import (
    AuthenticationResponse,
    MessageResponse,
    RegistrationResponse,
    UserResponse,
)
from backend.config.auth_config import AuthConfig
from backend.database.session import get_database_session
from backend.models.auth.user import User
from backend.services.auth.authentication_service import (
    AuthenticationResult,
    AuthenticationService,
)
from backend.services.auth.email_verification_service import (
    EmailVerificationService,
)
from backend.services.auth.registration_service import RegistrationService

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

_registration_service = RegistrationService()
_email_verification_service = EmailVerificationService()


def get_authentication_service() -> AuthenticationService:
    """
    Build authentication from validated environment settings.
    """

    return AuthenticationService(
        AuthConfig.from_environment(),
    )


def build_user_response(
    user: User,
) -> UserResponse:
    """
    Return only safe account fields.
    """

    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        country=user.country,
        is_email_verified=user.is_email_verified,
        created_at=user.created_at,
    )


def build_authentication_response(
    result: AuthenticationResult,
    config: AuthConfig,
    response: Response,
) -> AuthenticationResponse:
    """
    Store refresh token safely and return the short access token.
    """

    response.set_cookie(
        key=config.refresh_cookie_name,
        value=result.refresh_token,
        max_age=config.refresh_token_days * 24 * 60 * 60,
        httponly=True,
        secure=config.secure_cookies,
        samesite="strict",
        path="/auth",
    )

    return AuthenticationResponse(
        access_token=result.access_token,
        expires_in=config.access_token_minutes * 60,
        user=build_user_response(
            result.user,
        ),
    )


@auth_router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegistrationRequest,
    session: Session = Depends(
        get_database_session,
    ),
) -> RegistrationResponse:
    """
    Create an account after required consent.
    """

    try:
        user = _registration_service.register(
            request=request,
            session=session,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return RegistrationResponse(
        user=build_user_response(
            user,
        ),
        message=("Account created. Email verification is required before login."),
    )


@auth_router.post(
    "/login",
    response_model=AuthenticationResponse,
)
def login(
    request: LoginRequest,
    response: Response,
    session: Session = Depends(
        get_database_session,
    ),
) -> AuthenticationResponse:
    """
    Login and create one revocable device session.
    """

    config = AuthConfig.from_environment()

    try:
        result = get_authentication_service().login(
            email=str(
                request.email,
            ),
            password=request.password,
            device_name=request.device_name,
            session=session,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error

    return build_authentication_response(
        result=result,
        config=config,
        response=response,
    )


@auth_router.post(
    "/refresh",
    response_model=AuthenticationResponse,
)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None,
        alias="alphaedge_refresh",
    ),
    session: Session = Depends(
        get_database_session,
    ),
) -> AuthenticationResponse:
    """
    Rotate a refresh token and return a new access token.
    """

    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session is required.",
        )

    config = AuthConfig.from_environment()

    try:
        result = get_authentication_service().refresh(
            refresh_token=refresh_token,
            session=session,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error

    return build_authentication_response(
        result=result,
        config=config,
        response=response,
    )


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None,
        alias="alphaedge_refresh",
    ),
    session: Session = Depends(
        get_database_session,
    ),
) -> None:
    """
    Revoke the current device session.
    """

    config = AuthConfig.from_environment()

    if refresh_token is not None:
        get_authentication_service().logout(
            refresh_token=refresh_token,
            session=session,
        )

    response.delete_cookie(
        key=config.refresh_cookie_name,
        path="/auth",
    )


@auth_router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout_all(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None,
        alias="alphaedge_refresh",
    ),
    session: Session = Depends(
        get_database_session,
    ),
) -> None:
    """
    Revoke every active session for the current user.
    """

    config = AuthConfig.from_environment()

    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session is required.",
        )

    get_authentication_service().logout_all(
        refresh_token=refresh_token,
        session=session,
    )
    response.delete_cookie(
        key=config.refresh_cookie_name,
        path="/auth",
    )


@auth_router.post(
    "/email-verification/request",
    response_model=MessageResponse,
)
def request_email_verification(
    request: EmailVerificationRequest,
    session: Session = Depends(get_database_session),
) -> MessageResponse:
    """Create a local verification link without revealing account existence."""

    _email_verification_service.request_verification(
        email=str(request.email),
        session=session,
    )

    return MessageResponse(
        message=("If an eligible account exists, a verification link was created.")
    )


@auth_router.post(
    "/email-verification/verify",
    response_model=MessageResponse,
)
def verify_email(
    request: VerifyEmailRequest,
    session: Session = Depends(get_database_session),
) -> MessageResponse:
    """Verify one valid, unused email token."""

    try:
        _email_verification_service.verify(
            raw_token=request.token,
            session=session,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return MessageResponse(
        message="Email verified successfully.",
    )
