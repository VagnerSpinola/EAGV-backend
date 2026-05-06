"""add pending academy support tables

Revision ID: 20260506_0007
Revises: 20260506_0006
Create Date: 2026-05-06 00:50:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260506_0007"
down_revision = "20260506_0006"
branch_labels = None
depends_on = None


body_photo_type = sa.Enum("front", "side", "back", name="body_photo_type", native_enum=False)


def upgrade() -> None:
    op.create_table(
        "body_photos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("type", body_photo_type, nullable=False),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_body_photos_member_id"), "body_photos", ["member_id"], unique=False)

    op.create_table(
        "physical_assessments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("vo2_estimate", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("resting_heart_rate", sa.Integer(), nullable=True),
        sa.Column("flexibility_score", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("strength_score", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("posture_notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_physical_assessments_member_id"), "physical_assessments", ["member_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_physical_assessments_member_id"), table_name="physical_assessments")
    op.drop_table("physical_assessments")

    op.drop_index(op.f("ix_body_photos_member_id"), table_name="body_photos")
    op.drop_table("body_photos")