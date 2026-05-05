"""seed arena and sunset system settings

Revision ID: 20260505_0003
Revises: 20260505_0002
Create Date: 2026-05-05 00:45:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260505_0003"
down_revision = "20260505_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_system_settings_singleton", "system_settings", type_="check")

    op.add_column("system_settings", sa.Column("slug", sa.String(length=100), nullable=True))
    op.add_column("system_settings", sa.Column("sector", sa.String(length=50), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE system_settings
            SET
                slug = 'arena',
                sector = 'academia',
                system_name = 'Arena',
                short_name = 'Arena',
                tagline = 'Energia, disciplina e performance em uma identidade unica.',
                description = 'Arena e a configuracao da academia do ecossistema EAGV, pensada para recepcao, treinos, aulas e uma jornada visual forte desde o primeiro acesso.',
                logo_url = 'assets/images/arena_logo',
                logo_mark_url = 'assets/images/arena_logo_mark',
                favicon_url = 'assets/images/arena_logo_favicon',
                hero_image_url = 'assets/images/arena_hero',
                login_background_url = 'assets/images/arena_login_background',
                support_email = 'arena@eagv.com',
                support_phone = '+55 11 4100-1000',
                primary_color = '#F15A24',
                secondary_color = '#171717',
                default_locale = 'pt-BR',
                timezone = 'America/Sao_Paulo',
                is_maintenance_mode = false
            WHERE id = 1
            """
        )
    )

    op.execute(
        sa.text(
            """
            INSERT INTO system_settings (
                id,
                slug,
                sector,
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
                2,
                'sunset',
                'bar',
                'Sunset',
                'Sunset',
                'Um bar com atmosfera quente, social e memoravel desde a primeira tela.',
                'Sunset representa o ambiente do bar no EAGV, com foco em hospitalidade, ambientacao premium e uma linguagem visual pensada para noites movimentadas e atendimento rapido.',
                'assets/images/sunset_logo',
                'assets/images/sunset_logo_mark',
                'assets/images/sunset_logo_favicon',
                'assets/images/sunset_hero',
                'assets/images/sunset_login_background',
                'sunset@eagv.com',
                '+55 11 4100-2020',
                '#F2994A',
                '#2F4858',
                'pt-BR',
                'America/Sao_Paulo',
                false
            )
            """
        )
    )

    op.alter_column("system_settings", "slug", nullable=False)
    op.alter_column("system_settings", "sector", nullable=False)
    op.create_index(op.f("ix_system_settings_slug"), "system_settings", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_system_settings_slug"), table_name="system_settings")

    op.execute(sa.text("DELETE FROM system_settings WHERE id = 2"))

    op.execute(
        sa.text(
            """
            UPDATE system_settings
            SET
                slug = NULL,
                sector = NULL,
                system_name = 'EAGV Platform',
                short_name = 'EAGV',
                tagline = 'Controle operacional para ambientes conectados.',
                description = 'Configuracao publica inicial do sistema consumida pelo frontend no bootstrap da aplicacao.',
                logo_url = 'https://cdn.example.com/eagv/logo.svg',
                logo_mark_url = 'https://cdn.example.com/eagv/logo-mark.svg',
                favicon_url = 'https://cdn.example.com/eagv/favicon.ico',
                hero_image_url = 'https://cdn.example.com/eagv/hero.jpg',
                login_background_url = 'https://cdn.example.com/eagv/login-background.jpg',
                support_email = 'suporte@eagv.com',
                support_phone = '+55 11 4000-0000',
                primary_color = '#C9562A',
                secondary_color = '#417062',
                default_locale = 'pt-BR',
                timezone = 'America/Sao_Paulo',
                is_maintenance_mode = false
            WHERE id = 1
            """
        )
    )

    op.drop_column("system_settings", "sector")
    op.drop_column("system_settings", "slug")
    op.create_check_constraint("ck_system_settings_singleton", "system_settings", "id = 1")