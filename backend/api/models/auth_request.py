"""
Authentication request models.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegistrationRequest(BaseModel):
    """
    Safe minimum registration data.
    """

    full_name: str = Field(
        min_length=2,
        max_length=120,
    )
    email: EmailStr
    password: str = Field(
        min_length=12,
        max_length=128,
    )
    country: str = Field(
        min_length=2,
        max_length=2,
    )
    accepts_terms: bool
    accepts_risk_disclosure: bool
    confirms_adult: bool

    @field_validator(
        "full_name",
        "country",
        mode="before",
    )
    @classmethod
    def strip_text(
        cls,
        value: str,
    ) -> str:
        return value.strip()

    @field_validator(
        "country",
    )
    @classmethod
    def normalize_country(
        cls,
        value: str,
    ) -> str:
        return value.upper()


class LoginRequest(BaseModel):
    """
    Login credentials and an optional user-friendly device name.
    """

    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=128,
    )
    device_name: str | None = Field(
        default=None,
        max_length=120,
    )


class EmailVerificationRequest(BaseModel):
    """Request a new local development verification link."""

    email: EmailStr


class VerifyEmailRequest(BaseModel):
    """Consume a one-time email verification token."""

    token: str = Field(min_length=20, max_length=200)
