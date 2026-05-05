from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole, UserSector
from app.services.permissions import NavigationLevel


class SystemSettingsRead(BaseModel):
    id: int
    slug: str
    sector: str
    system_name: str
    short_name: str
    tagline: str | None
    description: str | None
    logo_url: str | None
    logo_mark_url: str | None
    favicon_url: str | None
    hero_image_url: str | None
    login_background_url: str | None
    support_email: str | None
    support_phone: str | None
    primary_color: str | None
    secondary_color: str | None
    default_locale: str
    timezone: str
    is_maintenance_mode: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PortalAccessRead(BaseModel):
    role: UserRole
    sector: UserSector | None
    can_access_portal: bool
    allowed_navigation_levels: list[NavigationLevel]
    profiles: list[SystemSettingsRead]