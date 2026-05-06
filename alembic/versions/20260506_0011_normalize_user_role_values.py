"""normalize user role values

Revision ID: 20260506_0011
Revises: 20260506_0010
Create Date: 2026-05-06 04:25:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260506_0011"
down_revision = "20260506_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE users
            SET role = lower(role)
            WHERE role IN ('ADMIN', 'STAFF', 'CLIENT')
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE users
            SET role = upper(role)
            WHERE role IN ('admin', 'staff', 'client')
            """
        )
    )