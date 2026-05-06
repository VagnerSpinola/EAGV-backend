"""add payment operator id

Revision ID: 20260506_0013
Revises: 20260506_0012
Create Date: 2026-05-06 22:40:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260506_0013"
down_revision = "20260506_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("operator_id", sa.Integer(), nullable=True))

    connection = op.get_bind()
    payment_count = connection.execute(sa.text("SELECT COUNT(1) FROM payments")).scalar_one()
    if payment_count:
        admin_user_id = connection.execute(
            sa.text("SELECT id FROM users WHERE role = 'admin' ORDER BY id LIMIT 1")
        ).scalar_one_or_none()
        if admin_user_id is None:
            raise RuntimeError("Could not backfill payments.operator_id because no admin user was found.")

        connection.execute(
            sa.text("UPDATE payments SET operator_id = :operator_id WHERE operator_id IS NULL"),
            {"operator_id": admin_user_id},
        )

    op.alter_column("payments", "operator_id", nullable=False)
    op.create_index(op.f("ix_payments_operator_id"), "payments", ["operator_id"], unique=False)
    op.create_foreign_key(
        "fk_payments_operator_id_users",
        "payments",
        "users",
        ["operator_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_payments_operator_id_users", "payments", type_="foreignkey")
    op.drop_index(op.f("ix_payments_operator_id"), table_name="payments")
    op.drop_column("payments", "operator_id")