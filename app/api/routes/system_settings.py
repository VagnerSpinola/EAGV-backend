from fastapi import APIRouter, File, UploadFile, status

from app.api.deps import CurrentAdmin, CurrentUser, DbSession
from app.schemas.system_settings import (
    PortalAccessRead,
    SystemSettingsAssetField,
    SystemSettingsAssetUploadResponse,
    SystemSettingsCreate,
    SystemSettingsRead,
    SystemSettingsUpdate,
)
from app.services.permissions import filter_system_settings_for_user, get_allowed_navigation_levels
from app.services.blob_storage import upload_system_settings_asset
from app.services.system_settings import (
    create_system_settings,
    get_system_settings_by_id,
    get_system_settings_by_slug,
    list_system_settings,
    update_system_settings,
    update_system_settings_asset_url,
)


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


@router.post("/settings", response_model=SystemSettingsRead, status_code=status.HTTP_201_CREATED)
def create_system_settings_profile(
    payload: SystemSettingsCreate,
    _: CurrentAdmin,
    db: DbSession,
) -> SystemSettingsRead:
    settings = create_system_settings(db, settings_in=payload)
    return SystemSettingsRead.model_validate(settings)


@router.put("/settings/{settings_id}", response_model=SystemSettingsRead)
def update_system_settings_profile(
    settings_id: int,
    payload: SystemSettingsUpdate,
    _: CurrentAdmin,
    db: DbSession,
) -> SystemSettingsRead:
    settings_profile = get_system_settings_by_id(db, settings_id=settings_id)
    settings = update_system_settings(db, settings_profile=settings_profile, settings_in=payload)
    return SystemSettingsRead.model_validate(settings)


@router.post(
    "/settings/{slug}/assets/{asset_field}",
    response_model=SystemSettingsAssetUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_system_settings_image(
    slug: str,
    asset_field: SystemSettingsAssetField,
    file: UploadFile = File(...),
    _: CurrentAdmin = None,
    db: DbSession = None,
) -> SystemSettingsAssetUploadResponse:
    settings_profile = get_system_settings_by_slug(db, slug=slug)
    asset_url = upload_system_settings_asset(file, slug=slug, asset_field=asset_field.value)
    updated_settings = update_system_settings_asset_url(
        db,
        settings_profile=settings_profile,
        asset_field=asset_field.value,
        asset_url=asset_url,
    )
    return SystemSettingsAssetUploadResponse(
        asset_field=asset_field,
        asset_url=asset_url,
        settings=SystemSettingsRead.model_validate(updated_settings),
    )