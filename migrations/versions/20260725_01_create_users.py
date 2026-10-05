"""
Create the minimum safe user account table.

Revision ID: 20260725_01
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "20260725_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create users and its unique email index.
    """

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(length=120),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=320),
            nullable=False,
        ),
        sa.Column(
            "country",
            sa.String(length=2),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "is_adult_confirmed",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "terms_accepted_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "risk_disclosure_accepted_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "is_email_verified",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "id",
        ),
    )
    op.create_index(
        op.f("ix_users_email"),
        "users",
        [
            "email",
        ],
        unique=True,
    )


def downgrade() -> None:
    """
    Remove the user account table.
    """

    op.drop_index(
        op.f("ix_users_email"),
        table_name="users",
    )
    op.drop_table(
        "users",
    )
