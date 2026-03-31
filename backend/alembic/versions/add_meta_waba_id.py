"""Add meta_waba_id to User

Revision ID: b1c2d3e4f5a6
Revises: 8a7f8c6b9e3d
Create Date: 2026-04-01
"""
from alembic import op
import sqlalchemy as sa

revision  = "b1c2d3e4f5a6"
down_revision = "8a7f8c6b9e3d"
branch_labels = None
depends_on    = None

def upgrade() -> None:
    op.add_column("user", sa.Column("meta_waba_id", sa.String(64), nullable=True))

def downgrade() -> None:
    op.drop_column("user", "meta_waba_id")