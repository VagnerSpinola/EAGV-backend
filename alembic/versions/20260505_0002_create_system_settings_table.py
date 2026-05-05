"""create system settings table

Revision ID: 20260505_0002
Revises: 20260505_0001
Create Date: 2026-05-05 00:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260505_0002"
down_revision = "20260505_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("system_name", sa.String(length=255), nullable=False),
        sa.Column("short_name", sa.String(length=100), nullable=False),
        sa.Column("tagline", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("logo_mark_url", sa.String(length=500), nullable=True),
        sa.Column("favicon_url", sa.String(length=500), nullable=True),
        sa.Column("hero_image_url", sa.String(length=500), nullable=True),
        sa.Column("login_background_url", sa.String(length=500), nullable=True),
        sa.Column("support_email", sa.String(length=255), nullable=True),
        sa.Column("support_phone", sa.String(length=50), nullable=True),
        sa.Column("primary_color", sa.String(length=20), nullable=True),
        sa.Column("secondary_color", sa.String(length=20), nullable=True),
        sa.Column("default_locale", sa.String(length=20), nullable=False, server_default="pt-BR"),
        sa.Column(
            "timezone",
            sa.String(length=100),
            nullable=False,
            server_default="America/Sao_Paulo",
        ),
        sa.Column("is_maintenance_mode", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("id = 1", name="ck_system_settings_singleton"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO system_settings (
                id,
                system_name,
                short_name,
                tagline,
                description,
                logo_url,
                logo_mark_url,
                favicon_url,
                hero_image_url,
                login_background_url,
                support_email,
                support_phone,
                primary_color,
                secondary_color,
                default_locale,
                timezone,
                is_maintenance_mode
            ) VALUES (
                1,
                'EAGV Platform',
                'EAGV',
                'Controle operacional para ambientes conectados.',
                'Configuracao publica inicial do sistema consumida pelo frontend no bootstrap da aplicacao.',
                'https://cdn.example.com/eagv/logo.svg',
                'https://cdn.example.com/eagv/logo-mark.svg',
                'https://cdn.example.com/eagv/favicon.ico',
                'https://cdn.example.com/eagv/hero.jpg',
                'https://cdn.example.com/eagv/login-background.jpg',
                'suporte@eagv.com',
                '+55 11 4000-0000',
                '#C9562A',
                '#417062',
                'pt-BR',
                'America/Sao_Paulo',
                false
            )
            """
        )
    )


def downgrade() -> None:
    op.drop_table("system_settings")