"""add payment class coverages

Revision ID: 20260507_0019
Revises: 20260507_0018
Create Date: 2026-05-07 15:55:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260507_0019"
down_revision = "20260507_0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payment_class_coverages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("class_title_snapshot", sa.String(length=160), nullable=False),
        sa.Column("plan_id_snapshot", sa.Integer(), nullable=False),
        sa.Column("plan_name_snapshot", sa.String(length=120), nullable=False),
        sa.Column("plan_price_snapshot", sa.Numeric(10, 2), nullable=False),
        sa.Column("plan_duration_days_snapshot", sa.Integer(), nullable=False),
        sa.Column("covered_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("covered_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_id", "class_id", name="uq_payment_class_coverages_payment_class"),
    )
    op.create_index(op.f("ix_payment_class_coverages_payment_id"), "payment_class_coverages", ["payment_id"], unique=False)
    op.create_index(op.f("ix_payment_class_coverages_class_id"), "payment_class_coverages", ["class_id"], unique=False)

    op.execute(
        """
        INSERT INTO payment_class_coverages (
            payment_id,
            class_id,
            class_title_snapshot,
            plan_id_snapshot,
            plan_name_snapshot,
            plan_price_snapshot,
            plan_duration_days_snapshot,
            covered_from,
            covered_until,
            created_at
        )
        SELECT
            payments.id,
            classes.id,
            classes.title,
            plans.id,
            plans.name,
            plans.price,
            plans.duration_days,
            payments.created_at,
            payments.created_at + make_interval(days => plans.duration_days),
            payments.created_at
        FROM payments
        JOIN member_class_assignments ON member_class_assignments.member_id = payments.member_id
        JOIN classes ON classes.id = member_class_assignments.class_id
        JOIN plans ON plans.id = classes.plan_id
        WHERE payments.status = 'success'
          AND member_class_assignments.assigned_at <= payments.created_at
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_payment_class_coverages_class_id"), table_name="payment_class_coverages")
    op.drop_index(op.f("ix_payment_class_coverages_payment_id"), table_name="payment_class_coverages")
    op.drop_table("payment_class_coverages")