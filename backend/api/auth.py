"""
Authentication API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.models.auth_request import RegistrationRequest
from backend.api.models.auth_response import RegistrationResponse, UserResponse
from backend.database.session import get_database_session
from backend.services.auth.registration_service import RegistrationService

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

_registration_service = RegistrationService()


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
        user=UserResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            country=user.country,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
        ),
        message=("Account created. Email verification is required before login."),
    )
