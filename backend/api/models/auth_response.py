"""
Authentication response models.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    """
    Public user account fields.
    """

    id: UUID
    full_name: str
    email: str
    country: str
    is_email_verified: bool
    created_at: datetime


class RegistrationResponse(BaseModel):
    """
    Successful registration response.
    """

    user: UserResponse
    message: str


class AuthenticationResponse(BaseModel):
    """
    Access token and safe account details.
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class MessageResponse(BaseModel):
    """Safe generic operation result."""

    message: str
