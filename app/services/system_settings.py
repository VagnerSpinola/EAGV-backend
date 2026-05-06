from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.system_settings import SystemSettings
from app.schemas.system_settings import SystemSettingsCreate, SystemSettingsUpdate


def list_system_settings(db: Session) -> list[SystemSettings]:
    statement = select(SystemSettings).order_by(SystemSettings.id.asc())
    settings = db.execute(statement).scalars().all()
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System settings have not been configured.",
        )

    return settings


def get_system_settings_by_slug(db: Session, slug: str) -> SystemSettings:
    statement = select(SystemSettings).where(SystemSettings.slug == slug)
    settings = db.execute(statement).scalar_one_or_none()
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System settings profile was not found.",
        )

    return settings


def get_system_settings_by_id(db: Session, settings_id: int) -> SystemSettings:
    statement = select(SystemSettings).where(SystemSettings.id == settings_id)
    settings = db.execute(statement).scalar_one_or_none()
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System settings profile was not found.",
        )

    return settings


def ensure_unique_system_settings_slug(db: Session, slug: str, *, exclude_id: int | None = None) -> None:
    statement = select(SystemSettings).where(SystemSettings.slug == slug)
    existing_settings = db.execute(statement).scalar_one_or_none()
    if existing_settings is None:
        return

    if exclude_id is not None and existing_settings.id == exclude_id:
        return

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="A system settings profile with this slug already exists.",
    )


def create_system_settings(db: Session, settings_in: SystemSettingsCreate) -> SystemSettings:
    ensure_unique_system_settings_slug(db, settings_in.slug)

    settings = SystemSettings(**settings_in.model_dump())
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_system_settings(
    db: Session,
    settings_profile: SystemSettings,
    settings_in: SystemSettingsUpdate,
) -> SystemSettings:
    ensure_unique_system_settings_slug(db, settings_in.slug, exclude_id=settings_profile.id)

    for field, value in settings_in.model_dump().items():
        setattr(settings_profile, field, value)

    db.add(settings_profile)
    db.commit()
    db.refresh(settings_profile)
    return settings_profile


def update_system_settings_asset_url(
    db: Session,
    settings_profile: SystemSettings,
    asset_field: str,
    asset_url: str,
) -> SystemSettings:
    setattr(settings_profile, asset_field, asset_url)
    db.add(settings_profile)
    db.commit()
    db.refresh(settings_profile)
    return settings_profile