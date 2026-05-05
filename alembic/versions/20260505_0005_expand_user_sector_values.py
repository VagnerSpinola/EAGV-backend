"""expand user sector values

Revision ID: 20260505_0005
Revises: 20260505_0004
Create Date: 2026-05-05 01:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260505_0005"
down_revision = "20260505_0004"
branch_labels = None
depends_on = None


NEW_ALLOWED_SECTORS = (
    "academia",
    "bar",
    "quadra_areia",
    "piscina",
    "suplemento",
    "roupas",
    "lanchonete",
    "admin",
    "recepcao",
    "manutencao",
    "geral",
)

OLD_ALLOWED_SECTORS = (
    "academia",
    "loja",
    "bar",
)


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            DO $$
            DECLARE
                sector_constraint_name text;
            BEGIN
                SELECT con.conname INTO sector_constraint_name
                FROM pg_constraint con
                JOIN pg_class rel ON rel.oid = con.conrelid
                WHERE rel.relname = 'users'
                  AND con.contype = 'c'
                  AND pg_get_constraintdef(con.oid) ILIKE '%sector%';

                IF sector_constraint_name IS NOT NULL THEN
                    EXECUTE format('ALTER TABLE users DROP CONSTRAINT %I', sector_constraint_name);
                END IF;
            END $$;
            """
        )
    )

    op.alter_column("users", "sector", type_=sa.String(length=50), existing_nullable=True)
    op.execute(sa.text("UPDATE users SET sector = LOWER(sector) WHERE sector IS NOT NULL"))
    op.execute(sa.text("UPDATE users SET sector = 'geral' WHERE sector = 'loja'"))
    op.create_check_constraint(
        "ck_users_sector_allowed",
        "users",
        "sector IS NULL OR sector IN ('academia', 'bar', 'quadra_areia', 'piscina', 'suplemento', 'roupas', 'lanchonete', 'admin', 'recepcao', 'manutencao', 'geral')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_sector_allowed", "users", type_="check")

    op.execute(
        sa.text(
            "UPDATE users SET sector = 'loja' WHERE sector = 'geral'"
        )
    )
    op.execute(
        sa.text(
            "UPDATE users SET sector = NULL WHERE sector IS NOT NULL AND sector NOT IN ('academia', 'loja', 'bar')"
        )
    )
    op.execute(sa.text("UPDATE users SET sector = UPPER(sector) WHERE sector IS NOT NULL"))

    op.create_check_constraint(
        "ck_users_sector_allowed",
        "users",
        "sector IS NULL OR sector IN ('ACADEMIA', 'LOJA', 'BAR')",
    )