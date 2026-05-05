from pathlib import Path
import sys
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.models.system_settings import SystemSettings
from app.models.user import User, UserRole, UserSector
from app.services.permissions import (
    NavigationLevel,
    filter_system_settings_for_user,
    get_allowed_navigation_levels,
)


def build_user(role: UserRole, sector: UserSector | None) -> User:
    return User(
        id=1,
        email="user@example.com",
        full_name="Example User",
        role=role,
        sector=sector,
        hashed_password="hashed",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def build_profile(profile_id: int, slug: str, sector: str) -> SystemSettings:
    return SystemSettings(
        id=profile_id,
        slug=slug,
        sector=sector,
        system_name=slug.title(),
        short_name=slug[:10],
        tagline=None,
        description=None,
        logo_url=None,
        logo_mark_url=None,
        favicon_url=None,
        hero_image_url=None,
        login_background_url=None,
        support_email=None,
        support_phone=None,
        primary_color=None,
        secondary_color=None,
        default_locale="pt-BR",
        timezone="America/Sao_Paulo",
        is_maintenance_mode=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_admin_can_access_all_profiles_and_levels() -> None:
    user = build_user(UserRole.ADMIN, UserSector.GERAL)
    profiles = [
        build_profile(1, "arena", "academia"),
        build_profile(2, "piscina", "piscina"),
    ]

    filtered = filter_system_settings_for_user(user, profiles)
    levels = get_allowed_navigation_levels(user)

    assert [profile.slug for profile in filtered] == ["arena", "piscina"]
    assert levels == [
        NavigationLevel.OVERVIEW,
        NavigationLevel.MANAGEMENT,
        NavigationLevel.OPERATIONS,
    ]


def test_staff_is_restricted_to_own_sector_and_operational_levels() -> None:
    user = build_user(UserRole.STAFF, UserSector.ACADEMIA)
    profiles = [
        build_profile(1, "arena", "academia"),
        build_profile(2, "piscina", "piscina"),
    ]

    filtered = filter_system_settings_for_user(user, profiles)
    levels = get_allowed_navigation_levels(user)

    assert [profile.slug for profile in filtered] == ["arena"]
    assert levels == [NavigationLevel.OVERVIEW, NavigationLevel.OPERATIONS]


def test_staff_quadra_areia_matches_quadra_public_profile_alias() -> None:
    user = build_user(UserRole.STAFF, UserSector.QUADRA_AREIA)
    profiles = [
        build_profile(1, "quadra-areia", "quadra"),
        build_profile(2, "piscina", "piscina"),
    ]

    filtered = filter_system_settings_for_user(user, profiles)

    assert [profile.slug for profile in filtered] == ["quadra-areia"]


def test_client_has_no_portal_access() -> None:
    user = build_user(UserRole.CLIENT, None)
    profiles = [build_profile(1, "arena", "academia")]

    assert filter_system_settings_for_user(user, profiles) == []
    assert get_allowed_navigation_levels(user) == []
