"""sync payment methods sequence

Revision ID: 20260506_0010
Revises: 20260506_0009
Create Date: 2026-05-06 04:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260506_0010"
down_revision = "20260506_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            SELECT setval(
                pg_get_serial_sequence('payment_methods', 'id'),
                COALESCE((SELECT MAX(id) FROM payment_methods), 1),
                true
            )
            """
        )
    )


def downgrade() -> None:
    pass