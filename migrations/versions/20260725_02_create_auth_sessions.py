"""
Create revocable multi-device authentication sessions.

Revision ID: 20260725_02
Revises: 20260725_01
"""

import sqlalchemy as sa
from alembic import op

revision = "20260725_02"
down_revision = "20260725_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_sessions",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "refresh_token_jti",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "device_name",
            sa.String(length=120),
            nullable=True,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "last_used_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            [
                "user_id",
            ],
            [
                "users.id",
            ],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
        ),
    )
    op.create_index(
        op.f("ix_auth_sessions_refresh_token_jti"),
        "auth_sessions",
        [
            "refresh_token_jti",
        ],
        unique=True,
    )
    op.create_index(
        op.f("ix_auth_sessions_user_id"),
        "auth_sessions",
        [
            "user_id",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_auth_sessions_user_id"),
        table_name="auth_sessions",
    )
    op.drop_index(
        op.f("ix_auth_sessions_refresh_token_jti"),
        table_name="auth_sessions",
    )
    op.drop_table(
        "auth_sessions",
    )
