"""
User account persistence model.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


def utc_now() -> datetime:
    """
    Return a timezone-aware UTC timestamp.
    """

    return datetime.now(UTC)


class User(Base):
    """
    Store the minimum approved user account information.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    full_name: Mapped[str] = mapped_column(
        String(120),
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
    )
    country: Mapped[str] = mapped_column(
        String(2),
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
    )
    is_adult_confirmed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    terms_accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    risk_disclosure_accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
