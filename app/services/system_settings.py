from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.system_settings import SystemSettings


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