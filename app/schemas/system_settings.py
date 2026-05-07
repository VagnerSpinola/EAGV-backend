from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.models.user import UserRole, UserSector
from app.services.permissions import NavigationLevel


class SystemSettingsAssetField(StrEnum):
    LOGO_URL = "logo_url"
    LOGO_MARK_URL = "logo_mark_url"
    FAVICON_URL = "favicon_url"
    HERO_IMAGE_URL = "hero_image_url"
    LOGIN_BACKGROUND_URL = "login_background_url"


class SystemSettingsWrite(BaseModel):
    slug: str
    sector: str
    system_name: str
    short_name: str
    tagline: str | None = None
    description: str | None = None
    logo_url: str | None = None
    logo_mark_url: str | None = None
    favicon_url: str | None = None
    hero_image_url: str | None = None
    login_background_url: str | None = None
    support_email: EmailStr | None = None
    support_phone: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    default_locale: str = "pt-BR"
    timezone: str = "America/Sao_Paulo"
    active: bool = True
    is_maintenance_mode: bool = False

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        normalized = value.strip().lower().replace(" ", "-")
        if not normalized:
            raise ValueError("Slug is required.")

        return normalized

    @field_validator("sector")
    @classmethod
    def normalize_sector(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("Sector is required.")

        return normalized


class SystemSettingsCreate(SystemSettingsWrite):
    pass


class SystemSettingsUpdate(SystemSettingsWrite):
    pass


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
    active: bool
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


class SystemSettingsAssetUploadResponse(BaseModel):
    asset_field: SystemSettingsAssetField
    asset_url: str
    settings: SystemSettingsRead