"""normalize payment success status

Revision ID: 20260506_0012
Revises: 20260506_0011
Create Date: 2026-05-06 22:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260506_0012"
down_revision = "20260506_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE payments
            SET status = CASE lower(status)
                WHEN 'paid' THEN 'success'
                WHEN 'success' THEN 'success'
                WHEN 'pending' THEN 'pending'
                WHEN 'failed' THEN 'failed'
                WHEN 'canceled' THEN 'canceled'
                ELSE status
            END
            """
        )
    )
    op.alter_column("payments", "status", server_default="success")

    op.execute(sa.text("ALTER TABLE payments DROP CONSTRAINT IF EXISTS payment_status"))
    op.execute(sa.text("ALTER TABLE payments DROP CONSTRAINT IF EXISTS ck_payments_status_payment_status"))
    op.create_check_constraint(
        "ck_payments_status_payment_status",
        "payments",
        "status IN ('success', 'pending', 'failed', 'canceled')",
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE payments
            SET status = CASE lower(status)
                WHEN 'success' THEN 'paid'
                WHEN 'pending' THEN 'pending'
                WHEN 'failed' THEN 'failed'
                WHEN 'canceled' THEN 'canceled'
                ELSE status
            END
            """
        )
    )
    op.alter_column("payments", "status", server_default="pending")

    op.drop_constraint("ck_payments_status_payment_status", "payments", type_="check")
    op.create_check_constraint(
        "ck_payments_status_payment_status",
        "payments",
        "status IN ('pending', 'paid', 'failed', 'canceled')",
    )