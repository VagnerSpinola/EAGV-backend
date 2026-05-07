from collections.abc import Sequence
from enum import StrEnum

from app.models.system_settings import SystemSettings
from app.models.user import User, UserRole


class NavigationLevel(StrEnum):
    OVERVIEW = "overview"
    MANAGEMENT = "management"
    OPERATIONS = "operations"


def normalize_sector(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()
    if normalized in {"quadra", "quadra_areia", "quadra-areia"}:
        return "quadra_areia"

    return normalized


def get_allowed_navigation_levels(user: User) -> list[NavigationLevel]:
    if user.role == UserRole.ADMIN:
        return [NavigationLevel.OVERVIEW, NavigationLevel.MANAGEMENT, NavigationLevel.OPERATIONS]

    if user.role == UserRole.STAFF:
        return [NavigationLevel.OVERVIEW, NavigationLevel.OPERATIONS]

    return []


def filter_system_settings_for_user(user: User, settings: Sequence[SystemSettings]) -> list[SystemSettings]:
    active_settings = [profile for profile in settings if profile.active]

    if user.role == UserRole.ADMIN:
        return list(active_settings)

    if user.role == UserRole.STAFF and user.sector is not None:
        user_sector = normalize_sector(user.sector)
        return [profile for profile in active_settings if normalize_sector(profile.sector) == user_sector]

    return []
