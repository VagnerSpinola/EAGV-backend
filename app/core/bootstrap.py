from collections.abc import Sequence

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine
from app.core.security import get_password_hash
from app.models import PaymentMethod, SystemSettings, User
from app.models.user import UserRole, UserSector


SYSTEM_SETTINGS_SEED: Sequence[dict[str, object]] = (
    {
        "id": 1,
        "slug": "arena",
        "sector": "academia",
        "system_name": "Arena One",
        "short_name": "Arena One",
        "tagline": "Treino, recepcao e performance com a identidade Arena One.",
        "description": "Modulo da academia com a marca Arena One, usado para recepcao, operacao de treinos, aulas e acompanhamento da jornada do aluno.",
        "logo_url": "assets/images/arena_one_logo.png",
        "logo_mark_url": "assets/images/arena_one_logo.png",
        "favicon_url": "assets/images/arena_one_logo.png",
        "hero_image_url": "assets/images/arena_one_logo.png",
        "login_background_url": "assets/images/arena_one_logo.png",
        "support_email": "arenaone@eagv.com",
        "support_phone": "+55 11 4100-1000",
        "primary_color": "#F15A24",
        "secondary_color": "#171717",
        "default_locale": "pt-BR",
        "timezone": "America/Sao_Paulo",
        "is_maintenance_mode": False,
    },
    {
        "id": 2,
        "slug": "sunset",
        "sector": "bar",
        "system_name": "Sunset Beach Club",
        "short_name": "Sunset",
        "tagline": "Hospitalidade, bar e atmosfera social com a marca Sunset Beach Club.",
        "description": "Modulo do bar com a identidade Sunset Beach Club, pensado para atendimento, consumo rapido e operacao social do espaco.",
        "logo_url": "assets/images/beach_club_logo.png",
        "logo_mark_url": "assets/images/beach_club_logo.png",
        "favicon_url": "assets/images/beach_club_logo.png",
        "hero_image_url": "assets/images/beach_club_logo.png",
        "login_background_url": "assets/images/beach_club_logo.png",
        "support_email": "sunset@eagv.com",
        "support_phone": "+55 11 4100-2020",
        "primary_color": "#F2994A",
        "secondary_color": "#2F4858",
        "default_locale": "pt-BR",
        "timezone": "America/Sao_Paulo",
        "is_maintenance_mode": False,
    },
    {
        "id": 3,
        "slug": "geral-user",
        "sector": "geral",
        "system_name": "EAGV",
        "short_name": "EAGV",
        "tagline": "Identidade principal e institucional do ecossistema EAGV.",
        "description": "Perfil matriz usado na experiencia institucional do sistema, com comunicacao centralizada e identidade visual unificada do EAGV.",
        "logo_url": "assets/images/eagv_logo.png",
        "logo_mark_url": "assets/images/eagv_logo.png",
        "favicon_url": "assets/images/eagv_logo.png",
        "hero_image_url": "assets/images/eagv_logo.png",
        "login_background_url": "assets/images/eagv_logo.png",
        "support_email": "contato@eagv.com",
        "support_phone": "+55 11 4100-0001",
        "primary_color": "#C9562A",
        "secondary_color": "#2F4858",
        "default_locale": "pt-BR",
        "timezone": "America/Sao_Paulo",
        "is_maintenance_mode": False,
    },
    {
        "id": 4,
        "slug": "loja-suplemento",
        "sector": "suplemento",
        "system_name": "Nutri Core",
        "short_name": "Nutri Core",
        "tagline": "Suplementacao e performance com a identidade Nutri Core.",
        "description": "Modulo comercial de suplementos com a marca Nutri Core, voltado para produtos de alta performance e atendimento consultivo.",
        "logo_url": "assets/images/nutri_core_logo.png",
        "logo_mark_url": "assets/images/nutri_core_logo.png",
        "favicon_url": "assets/images/nutri_core_logo.png",
        "hero_image_url": "assets/images/nutri_core_logo.png",
        "login_background_url": "assets/images/nutri_core_logo.png",
        "support_email": "nutricore@eagv.com",
        "support_phone": "+55 11 4100-3001",
        "primary_color": "#6C4CF1",
        "secondary_color": "#1D1B2F",
        "default_locale": "pt-BR",
        "timezone": "America/Sao_Paulo",
        "is_maintenance_mode": False,
    },
    {
        "id": 5,
        "slug": "loja-roupas",
        "sector": "roupas",
        "system_name": "Urban Fit Wear",
        "short_name": "Urban Fit",
        "tagline": "Moda esportiva com a identidade Urban Fit Wear.",
        "description": "Modulo de roupas com a marca Urban Fit Wear, focado em colecoes, vitrine digital e operacao comercial do vestuario.",
        "logo_url": "assets/images/urban_fit_wear_logo.png",
        "logo_mark_url": "assets/images/urban_fit_wear_logo.png",
        "favicon_url": "assets/images/urban_fit_wear_logo.png",
        "hero_image_url": "assets/images/urban_fit_wear_logo.png",
        "login_background_url": "assets/images/urban_fit_wear_logo.png",
        "support_email": "urbanfit@eagv.com",
        "support_phone": "+55 11 4100-3002",
        "primary_color": "#3F8EFC",
        "secondary_color": "#1C2942",
        "default_locale": "pt-BR",
        "timezone": "America/Sao_Paulo",
        "is_maintenance_mode": False,
    },
    {
        "id": 6,
        "slug": "lanchonete",
        "sector": "lanchonete",
        "system_name": "Fuel Station",
        "short_name": "Fuel Station",
        "tagline": "Snack bar e atendimento rapido com a identidade Fuel Station.",
        "description": "Modulo da lanchonete com a marca Fuel Station, preparado para pedidos rapidos, consumo casual e operacao diaria do ponto de apoio.",
        "logo_url": "assets/images/fuel_station_logo.png",
        "logo_mark_url": "assets/images/fuel_station_logo.png",
        "favicon_url": "assets/images/fuel_station_logo.png",
        "hero_image_url": "assets/images/fuel_station_logo.png",
        "login_background_url": "assets/images/fuel_station_logo.png",
        "support_email": "fuelstation@eagv.com",
        "support_phone": "+55 11 4100-4001",
        "primary_color": "#F97316",
        "secondary_color": "#5B3422",
        "default_locale": "pt-BR",
        "timezone": "America/Sao_Paulo",
        "is_maintenance_mode": False,
    },
    {
        "id": 7,
        "slug": "piscina",
        "sector": "piscina",
        "system_name": "Agua Club",
        "short_name": "Agua Club",
        "tagline": "Piscina, lazer e operacao com a identidade Agua Club.",
        "description": "Modulo da piscina com a marca Agua Club, pensado para controle de acesso, operacao aquatica e experiencia de lazer.",
        "logo_url": "assets/images/agua_club_logo.png",
        "logo_mark_url": "assets/images/agua_club_logo.png",
        "favicon_url": "assets/images/agua_club_logo.png",
        "hero_image_url": "assets/images/agua_club_logo.png",
        "login_background_url": "assets/images/agua_club_logo.png",
        "support_email": "aguaclub@eagv.com",
        "support_phone": "+55 11 4100-5001",
        "primary_color": "#00A6C8",
        "secondary_color": "#0D3B66",
        "default_locale": "pt-BR",
        "timezone": "America/Sao_Paulo",
        "is_maintenance_mode": False,
    },
    {
        "id": 8,
        "slug": "quadra-areia",
        "sector": "quadra_areia",
        "system_name": "Sand Court Arena",
        "short_name": "Sand Court",
        "tagline": "Esporte de areia e reservas com a identidade Sand Court Arena.",
        "description": "Modulo da quadra de areia com a marca Sand Court Arena, preparado para reservas, eventos e operacao esportiva ao ar livre.",
        "logo_url": "assets/images/arena_beach_sports_court.png",
        "logo_mark_url": "assets/images/arena_beach_sports_court.png",
        "favicon_url": "assets/images/arena_beach_sports_court.png",
        "hero_image_url": "assets/images/arena_beach_sports_court.png",
        "login_background_url": "assets/images/arena_beach_sports_court.png",
        "support_email": "sandcourt@eagv.com",
        "support_phone": "+55 11 4100-5002",
        "primary_color": "#D9A441",
        "secondary_color": "#6B4F2A",
        "default_locale": "pt-BR",
        "timezone": "America/Sao_Paulo",
        "is_maintenance_mode": False,
    },
    {
        "id": 9,
        "slug": "administracao",
        "sector": "admin",
        "system_name": "Centro Administrativo",
        "short_name": "Administracao",
        "tagline": "Operacao interna, retaguarda e gestao institucional do EAGV.",
        "description": "Modulo administrativo para operacao interna, acompanhamento institucional e rotinas do time de administracao.",
        "logo_url": "assets/images/eagv_logo.png",
        "logo_mark_url": "assets/images/eagv_logo.png",
        "favicon_url": "assets/images/eagv_logo.png",
        "hero_image_url": "assets/images/eagv_logo.png",
        "login_background_url": "assets/images/eagv_logo.png",
        "support_email": "admin@eagv.com",
        "support_phone": "+55 11 4100-0002",
        "primary_color": "#3C4557",
        "secondary_color": "#D9A441",
        "default_locale": "pt-BR",
        "timezone": "America/Sao_Paulo",
        "active": True,
        "is_maintenance_mode": False,
    },
)

PAYMENT_METHODS_SEED: Sequence[dict[str, object]] = (
    {"id": 1, "description": "PIX"},
    {"id": 2, "description": "CARD"},
)


def initialize_application_data() -> None:
    if not settings.database_auto_initialize:
        return

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        _seed_system_settings(session)
        _seed_payment_methods(session)
        _seed_admin_user(session)
        session.commit()


def _seed_system_settings(session: Session) -> None:
    existing_settings = {
        item.slug: item
        for item in session.execute(select(SystemSettings)).scalars().all()
    }

    for payload in SYSTEM_SETTINGS_SEED:
        slug = str(payload["slug"])
        current = existing_settings.get(slug)
        if current is None:
            session.add(SystemSettings(**payload))
            continue

        for field, value in payload.items():
            setattr(current, field, value)


def _seed_payment_methods(session: Session) -> None:
    existing_methods = {
        item.id: item
        for item in session.execute(select(PaymentMethod)).scalars().all()
    }

    for payload in PAYMENT_METHODS_SEED:
        current = existing_methods.get(int(payload["id"]))
        if current is None:
            session.add(PaymentMethod(**payload))
            continue

        current.description = str(payload["description"])

    session.flush()
    session.execute(
        text(
            """
            SELECT setval(
                pg_get_serial_sequence('payment_methods', 'id'),
                COALESCE((SELECT MAX(id) FROM payment_methods), 1),
                true
            )
            """
        )
    )


def _seed_admin_user(session: Session) -> None:
    if not settings.bootstrap_admin_email or not settings.bootstrap_admin_password:
        return

    existing_user = session.execute(
        select(User).where(User.email == settings.bootstrap_admin_email)
    ).scalar_one_or_none()
    if existing_user is not None:
        return

    session.add(
        User(
            email=settings.bootstrap_admin_email,
            full_name=settings.bootstrap_admin_full_name,
            role=UserRole.ADMIN,
            sector=UserSector.ADMIN,
            hashed_password=get_password_hash(settings.bootstrap_admin_password),
            is_active=True,
        )
    )