"""seed additional public system setting profiles

Revision ID: 20260505_0004
Revises: 20260505_0003
Create Date: 2026-05-05 01:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260505_0004"
down_revision = "20260505_0003"
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
                is_maintenance_mode
            ) VALUES
            (
                3,
                'geral-user',
                'geral',
                'EAGV',
                'EAGV',
                'A configuracao matriz para usuarios gerais do ecossistema EAGV.',
                'Perfil institucional do sistema, pensado para a experiencia geral do usuario com identidade unificada, inicio limpo e comunicacao clara entre todas as operacoes conectadas.',
                'assets/images/eagv_logo',
                'assets/images/eagv_logo_mark',
                'assets/images/eagv_favicon',
                'assets/images/eagv_hero',
                'assets/images/eagv_login_background',
                'contato@eagv.com',
                '+55 11 4100-0001',
                '#C9562A',
                '#2F4858',
                'pt-BR',
                'America/Sao_Paulo',
                false
            ),
            (
                4,
                'loja-suplemento',
                'loja',
                'Loja Suplemento',
                'Suplemento',
                'Forca comercial com linguagem de performance e nutricao esportiva.',
                'Perfil dedicado para a loja de suplementos, com uma identidade focada em energia, conversao e confianca para produtos de alta performance.',
                'assets/images/suplemento_logo',
                'assets/images/suplemento_logo_mark',
                'assets/images/suplemento_favicon',
                'assets/images/suplemento_hero',
                'assets/images/suplemento_login_background',
                'suplemento@eagv.com',
                '+55 11 4100-3001',
                '#6C4CF1',
                '#1D1B2F',
                'pt-BR',
                'America/Sao_Paulo',
                false
            ),
            (
                5,
                'loja-roupas',
                'loja',
                'Loja Roupas',
                'Roupas',
                'Moda esportiva e casual com uma apresentacao direta e sofisticada.',
                'Perfil para a loja de roupas do ecossistema, com foco em vitrines digitais, colecoes e uma navegacao leve para operacao comercial e atendimento.',
                'assets/images/roupas_logo',
                'assets/images/roupas_logo_mark',
                'assets/images/roupas_favicon',
                'assets/images/roupas_hero',
                'assets/images/roupas_login_background',
                'roupas@eagv.com',
                '+55 11 4100-3002',
                '#3F8EFC',
                '#1C2942',
                'pt-BR',
                'America/Sao_Paulo',
                false
            ),
            (
                6,
                'lanchonete',
                'lanchonete',
                'Lanchonete',
                'Lanchonete',
                'Atendimento rapido, cardapio enxuto e identidade acolhedora.',
                'Perfil operacional da lanchonete com linguagem visual calorosa, preparado para pedidos, consumo rapido e uma experiencia mais casual dentro do sistema.',
                'assets/images/lanchonete_logo',
                'assets/images/lanchonete_logo_mark',
                'assets/images/lanchonete_favicon',
                'assets/images/lanchonete_hero',
                'assets/images/lanchonete_login_background',
                'lanchonete@eagv.com',
                '+55 11 4100-4001',
                '#F97316',
                '#5B3422',
                'pt-BR',
                'America/Sao_Paulo',
                false
            ),
            (
                7,
                'piscina',
                'piscina',
                'Piscina',
                'Piscina',
                'Leveza visual, seguranca operacional e clima de bem-estar.',
                'Perfil pensado para a area de piscina, com atmosfera limpa, frescor visual e espaco para operacao de acesso, aulas aquaticas e servicos complementares.',
                'assets/images/piscina_logo',
                'assets/images/piscina_logo_mark',
                'assets/images/piscina_favicon',
                'assets/images/piscina_hero',
                'assets/images/piscina_login_background',
                'piscina@eagv.com',
                '+55 11 4100-5001',
                '#00A6C8',
                '#0D3B66',
                'pt-BR',
                'America/Sao_Paulo',
                false
            ),
            (
                8,
                'quadra-areia',
                'quadra',
                'Quadra de Areia',
                'Quadra',
                'Esporte ao ar livre com identidade vibrante e leitura imediata.',
                'Perfil da quadra de areia com foco em reservas, eventos, turmas e uma comunicacao visual mais ensolarada, competitiva e energica.',
                'assets/images/quadra_areia_logo',
                'assets/images/quadra_areia_logo_mark',
                'assets/images/quadra_areia_favicon',
                'assets/images/quadra_areia_hero',
                'assets/images/quadra_areia_login_background',
                'quadra@eagv.com',
                '+55 11 4100-5002',
                '#D9A441',
                '#6B4F2A',
                'pt-BR',
                'America/Sao_Paulo',
                false
            )
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM system_settings WHERE id IN (3, 4, 5, 6, 7, 8)"
        )
    )