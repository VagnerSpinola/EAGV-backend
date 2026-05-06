"""add academy core tables

Revision ID: 20260506_0006
Revises: 20260506_0005
Create Date: 2026-05-06 00:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260506_0006"
down_revision = "20260506_0005"
branch_labels = None
depends_on = None


member_status = sa.Enum("active", "inactive", "blocked", name="member_status", native_enum=False)
payment_method = sa.Enum("pix", "card", name="payment_method", native_enum=False)
payment_status = sa.Enum("pending", "paid", "failed", "canceled", name="payment_status", native_enum=False)
checkin_type = sa.Enum("gym", "pool", "court", name="checkin_type", native_enum=False)


def upgrade() -> None:
    op.execute(sa.text("ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_sector_allowed"))
    op.execute(sa.text("ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_sector_required_for_non_client"))
    op.create_check_constraint(
        "ck_users_sector_allowed",
        "users",
        "sector IS NULL OR sector IN ('academia', 'bar', 'quadra_areia', 'piscina', 'suplemento', 'roupas', 'lanchonete', 'admin', 'recepcao', 'manutencao', 'geral')",
    )
    op.create_check_constraint(
        "ck_users_sector_required_for_non_client",
        "users",
        "role = 'client' OR sector IS NOT NULL",
    )

    op.create_table(
        "members",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("cpf", sa.String(length=14), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("gender", sa.String(length=30), nullable=False),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("street", sa.String(length=255), nullable=False),
        sa.Column("number", sa.String(length=30), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False, server_default="Tabapua"),
        sa.Column("state", sa.String(length=100), nullable=False, server_default="Sao Paulo"),
        sa.Column("country", sa.String(length=100), nullable=False, server_default="Brasil"),
        sa.Column("zip_code", sa.String(length=20), nullable=False),
        sa.Column("status", member_status, nullable=False, server_default="active"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_members_cpf"), "members", ["cpf"], unique=True)
    op.create_index(op.f("ix_members_user_id"), "members", ["user_id"], unique=False)

    op.create_table(
        "plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("method", payment_method, nullable=False),
        sa.Column("status", payment_status, nullable=False, server_default="pending"),
        sa.Column("idempotency_key", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index(op.f("ix_payments_idempotency_key"), "payments", ["idempotency_key"], unique=True)
    op.create_index(op.f("ix_payments_member_id"), "payments", ["member_id"], unique=False)

    op.create_table(
        "checkins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("checkin_datetime", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("checkout_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("type", checkin_type, nullable=False),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_checkins_member_id"), "checkins", ["member_id"], unique=False)

    op.create_table(
        "body_measurements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("weight", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("height", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("body_fat_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("muscle_mass", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("chest", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("waist", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("hips", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("arm_left", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("arm_right", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("thigh_left", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("thigh_right", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("calf_left", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("calf_right", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_body_measurements_member_id"), "body_measurements", ["member_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_body_measurements_member_id"), table_name="body_measurements")
    op.drop_table("body_measurements")

    op.drop_index(op.f("ix_checkins_member_id"), table_name="checkins")
    op.drop_table("checkins")

    op.drop_index(op.f("ix_payments_member_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_idempotency_key"), table_name="payments")
    op.drop_table("payments")

    op.drop_table("plans")

    op.drop_index(op.f("ix_members_user_id"), table_name="members")
    op.drop_index(op.f("ix_members_cpf"), table_name="members")
    op.drop_table("members")

    op.execute(sa.text("ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_sector_required_for_non_client"))
    op.execute(sa.text("ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_sector_allowed"))
    op.create_check_constraint(
        "ck_users_sector_allowed",
        "users",
        "sector IS NULL OR sector IN ('academia', 'bar', 'quadra_areia', 'piscina', 'suplemento', 'roupas', 'lanchonete', 'admin', 'recepcao', 'manutencao', 'geral')",
    )