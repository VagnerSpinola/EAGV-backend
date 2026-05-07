from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.academy import Member
from app.models.nutrition import LabExam, MealPlan, NutritionProfile, NutritionProgress, Supplement
from app.models.user import User
from app.schemas.nutrition import MealPlanCreate, NutritionProfileCreate, NutritionProgressCreate


def _ensure_member_exists(db: Session, member_id: UUID) -> None:
    if db.get(Member, member_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")


def _ensure_user_exists(db: Session, user_id: int) -> None:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")


def _ensure_nutrition_profile_exists(db: Session, profile_id: UUID) -> NutritionProfile:
    profile = db.get(NutritionProfile, profile_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrition profile not found.")

    return profile


def list_nutrition_profiles(db: Session, *, member_id: UUID | None = None) -> list[NutritionProfile]:
    statement = select(NutritionProfile)
    if member_id is not None:
        statement = statement.where(NutritionProfile.member_id == member_id)

    return db.execute(statement.order_by(NutritionProfile.created_at.desc())).scalars().all()


def create_nutrition_profile(db: Session, payload: NutritionProfileCreate) -> NutritionProfile:
    _ensure_member_exists(db, payload.member_id)
    _ensure_user_exists(db, payload.nutritionist_id)

    profile = NutritionProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def list_meal_plans(db: Session, *, nutrition_profile_id: UUID | None = None) -> list[MealPlan]:
    statement = select(MealPlan)
    if nutrition_profile_id is not None:
        statement = statement.where(MealPlan.nutrition_profile_id == nutrition_profile_id)

    return db.execute(statement.order_by(MealPlan.created_at.desc())).scalars().all()


def create_meal_plan(db: Session, payload: MealPlanCreate) -> MealPlan:
    _ensure_nutrition_profile_exists(db, payload.nutrition_profile_id)

    meal_plan = MealPlan(**payload.model_dump())
    db.add(meal_plan)
    db.commit()
    db.refresh(meal_plan)
    return meal_plan


def list_nutrition_progress_entries(
    db: Session,
    *,
    nutrition_profile_id: UUID | None = None,
) -> list[NutritionProgress]:
    statement = select(NutritionProgress)
    if nutrition_profile_id is not None:
        statement = statement.where(NutritionProgress.nutrition_profile_id == nutrition_profile_id)

    return db.execute(statement.order_by(NutritionProgress.recorded_at.desc())).scalars().all()


def create_nutrition_progress(db: Session, payload: NutritionProgressCreate) -> NutritionProgress:
    _ensure_nutrition_profile_exists(db, payload.nutrition_profile_id)

    progress_payload = payload.model_dump()
    if progress_payload["recorded_at"] is None:
        progress_payload["recorded_at"] = datetime.now(timezone.utc)

    progress = NutritionProgress(**progress_payload)
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


def get_nutrition_overview(db: Session) -> dict[str, int]:
    return {
        "profile_count": db.scalar(select(func.count()).select_from(NutritionProfile)) or 0,
        "meal_plan_count": db.scalar(select(func.count()).select_from(MealPlan)) or 0,
        "progress_entry_count": db.scalar(select(func.count()).select_from(NutritionProgress)) or 0,
        "supplement_count": db.scalar(select(func.count()).select_from(Supplement)) or 0,
        "lab_exam_count": db.scalar(select(func.count()).select_from(LabExam)) or 0,
    }