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
