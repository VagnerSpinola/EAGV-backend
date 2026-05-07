"""add member class assignments

Revision ID: 20260507_0017
Revises: 20260507_0016
Create Date: 2026-05-07 11:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260507_0017"
down_revision = "20260507_0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "member_class_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("assigned_by", sa.Integer(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("member_id", "class_id", name="uq_member_class_assignments_member_class"),
    )
    op.create_index(op.f("ix_member_class_assignments_member_id"), "member_class_assignments", ["member_id"], unique=False)
    op.create_index(op.f("ix_member_class_assignments_class_id"), "member_class_assignments", ["class_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_member_class_assignments_class_id"), table_name="member_class_assignments")
    op.drop_index(op.f("ix_member_class_assignments_member_id"), table_name="member_class_assignments")
    op.drop_table("member_class_assignments")