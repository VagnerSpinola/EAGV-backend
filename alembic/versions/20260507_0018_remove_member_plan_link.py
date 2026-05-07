"""remove member plan link

Revision ID: 20260507_0018
Revises: 20260507_0017
Create Date: 2026-05-07 13:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260507_0018"
down_revision = "20260507_0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("fk_members_plan_id_plans", "members", type_="foreignkey")
    op.drop_index(op.f("ix_members_plan_id"), table_name="members")
    op.drop_column("members", "plan_id")


def downgrade() -> None:
    op.add_column("members", sa.Column("plan_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_members_plan_id"), "members", ["plan_id"], unique=False)
    op.create_foreign_key(
        "fk_members_plan_id_plans",
        "members",
        "plans",
        ["plan_id"],
        ["id"],
        ondelete="SET NULL",
    )