"""seed admin system settings

Revision ID: 20260507_0023
Revises: 20260507_0022
Create Date: 2026-05-07 21:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260507_0023"
down_revision = "20260507_0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
                active,
                is_maintenance_mode
            )
            SELECT
                9,
                'administracao',
                'admin',
                'Centro Administrativo',
                'Administracao',
                'Operacao interna, retaguarda e gestao institucional do EAGV.',
                'Modulo administrativo para operacao interna, acompanhamento institucional e rotinas do time de administracao.',
                'assets/images/eagv_logo.png',
                'assets/images/eagv_logo.png',
                'assets/images/eagv_logo.png',
                'assets/images/eagv_logo.png',
                'assets/images/eagv_logo.png',
                'admin@eagv.com',
                '+55 11 4100-0002',
                '#3C4557',
                '#D9A441',
                'pt-BR',
                'America/Sao_Paulo',
                TRUE,
                FALSE
            WHERE NOT EXISTS (
                SELECT 1 FROM system_settings WHERE slug = 'administracao'
            )
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM system_settings WHERE slug = 'administracao'"))