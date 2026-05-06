"""add user image url

Revision ID: 20260506_0005
Revises: 20260505_0004
Create Date: 2026-05-06 13:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260506_0005"
down_revision = "20260505_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "image_url")