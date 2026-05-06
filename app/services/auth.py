from datetime import timedelta

from jwt import InvalidTokenError
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    get_password_hash,
    verify_password,
)
from app.models.academy import Member
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserProfileUpdate


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.execute(statement).scalar_one_or_none()


def create_user(db: Session, user_in: UserCreate, *, auto_commit: bool = True) -> User:
    existing_user = get_user_by_email(db, email=user_in.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    if user_in.role != UserRole.CLIENT and user_in.sector is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sector is required for non-client users.",
        )

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        image_url=user_in.image_url,
        role=user_in.role,
        sector=user_in.sector,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    if auto_commit:
        db.commit()
    else:
        db.flush()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email=email)
    if user is None or not user.is_active:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def issue_access_token(subject: str) -> str:
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    return create_access_token(subject=subject, expires_delta=expires_delta)


def issue_password_reset_token(db: Session, email: str) -> str | None:
    user = get_user_by_email(db, email=email)
    if user is None or not user.is_active:
        return None

    return create_password_reset_token(subject=user.email)


def reset_user_password(db: Session, token: str, new_password: str) -> None:
    try:
        payload = decode_password_reset_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token is invalid or expired.",
        ) from exc

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token is missing the subject.",
        )

    user = get_user_by_email(db, email=email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for the provided reset token.",
        )

    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()


def update_current_user(db: Session, user: User, user_in: UserProfileUpdate) -> User:
    if "email" in user_in.model_fields_set and user_in.email != user.email:
        existing_user = get_user_by_email(db, email=user_in.email)
        if existing_user is not None and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )
        user.email = user_in.email

    if "full_name" in user_in.model_fields_set:
        user.full_name = user_in.full_name

    if "sector" in user_in.model_fields_set:
        if user.role != UserRole.CLIENT and user_in.sector is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Sector is required for non-client users.",
            )
        user.sector = user_in.sector

    if user_in.current_password and user_in.new_password:
        if not verify_password(user_in.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        user.hashed_password = get_password_hash(user_in.new_password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    return db.execute(statement).scalar_one_or_none()


def update_user_image(db: Session, user: User, image_url: str) -> User:
    user.image_url = image_url
    member = db.execute(select(Member).where(Member.user_id == user.id)).scalar_one_or_none()
    if member is not None:
        member.photo_url = image_url
        db.add(member)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user