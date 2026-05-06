"""add payment methods catalog

Revision ID: 20260506_0009
Revises: 20260506_0008
Create Date: 2026-05-06 03:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260506_0009"
down_revision = "20260506_0008"
branch_labels = None
depends_on = None


payment_method_enum = sa.Enum("pix", "card", name="payment_method", native_enum=False)


def upgrade() -> None:
    op.create_table(
        "payment_methods",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("description"),
    )
    op.bulk_insert(
        sa.table(
            "payment_methods",
            sa.column("id", sa.Integer()),
            sa.column("description", sa.String()),
        ),
        [
            {"id": 1, "description": "PIX"},
            {"id": 2, "description": "CARD"},
        ],
    )

    op.add_column("payments", sa.Column("method_id", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE payments
            SET method_id = CASE
                WHEN lower(method) = 'pix' THEN 1
                WHEN lower(method) = 'card' THEN 2
                ELSE NULL
            END
            """
        )
    )
    op.alter_column("payments", "method_id", nullable=False)
    op.create_index(op.f("ix_payments_method_id"), "payments", ["method_id"], unique=False)
    op.create_foreign_key(
        "fk_payments_method_id_payment_methods",
        "payments",
        "payment_methods",
        ["method_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.drop_column("payments", "method")


def downgrade() -> None:
    op.add_column("payments", sa.Column("method", payment_method_enum, nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE payments
            SET method = CASE method_id
                WHEN 1 THEN 'pix'
                WHEN 2 THEN 'card'
                ELSE NULL
            END
            """
        )
    )
    op.alter_column("payments", "method", nullable=False)
    op.drop_constraint("fk_payments_method_id_payment_methods", "payments", type_="foreignkey")
    op.drop_index(op.f("ix_payments_method_id"), table_name="payments")
    op.drop_column("payments", "method_id")
    op.drop_table("payment_methods")