from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.system_settings import PortalAccessRead, SystemSettingsRead
from app.services.permissions import filter_system_settings_for_user, get_allowed_navigation_levels
from app.services.system_settings import get_system_settings_by_slug, list_system_settings


router = APIRouter()


@router.get("/settings", response_model=list[SystemSettingsRead])
def read_system_settings(db: DbSession) -> list[SystemSettingsRead]:
    settings = list_system_settings(db)
    return [SystemSettingsRead.model_validate(item) for item in settings]


@router.get("/portal-access", response_model=PortalAccessRead)
def read_portal_access(current_user: CurrentUser, db: DbSession) -> PortalAccessRead:
    settings = list_system_settings(db)
    allowed_profiles = filter_system_settings_for_user(current_user, settings)
    return PortalAccessRead(
        role=current_user.role,
        sector=current_user.sector,
        can_access_portal=bool(allowed_profiles),
        allowed_navigation_levels=get_allowed_navigation_levels(current_user),
        profiles=[SystemSettingsRead.model_validate(item) for item in allowed_profiles],
    )


@router.get("/settings/{slug}", response_model=SystemSettingsRead)
def read_system_settings_by_slug(slug: str, db: DbSession) -> SystemSettingsRead:
    settings = get_system_settings_by_slug(db, slug=slug)
    return SystemSettingsRead.model_validate(settings)