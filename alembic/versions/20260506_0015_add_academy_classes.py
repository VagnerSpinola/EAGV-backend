"""add academy classes

Revision ID: 20260506_0015
Revises: 20260506_0014
Create Date: 2026-05-06 23:55:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260506_0015"
down_revision = "20260506_0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "classes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("frequency", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("days", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_classes_plan_id"), "classes", ["plan_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_classes_plan_id"), table_name="classes")
    op.drop_table("classes")