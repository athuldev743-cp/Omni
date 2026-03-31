"""Add whatsapp_uid to Lead

Revision ID: 8a7f8c6b9e3d
Revises: None
Create Date: 2026-03-31
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "8a7f8c6b9e3d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lead",
        sa.Column("whatsapp_uid", sa.String(length=128), nullable=True),
    )
    op.create_index(
        "ix_whatsapp_uid",
        "lead",
        ["whatsapp_uid"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_whatsapp_uid", table_name="lead")
    op.drop_column("lead", "whatsapp_uid")

