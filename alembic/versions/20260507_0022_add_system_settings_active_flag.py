"""add system settings active flag

Revision ID: 20260507_0022
Revises: 20260507_0021
Create Date: 2026-05-07 20:55:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260507_0022"
down_revision = "20260507_0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "system_settings",
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.execute(sa.text("UPDATE system_settings SET active = TRUE WHERE active IS NULL"))
    op.alter_column("system_settings", "active", server_default=None)


def downgrade() -> None:
    op.drop_column("system_settings", "active")