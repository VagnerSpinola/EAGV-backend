from uuid import UUID

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.nutrition import (
    MealPlanCreate,
    MealPlanRead,
    NutritionOverviewRead,
    NutritionProfileCreate,
    NutritionProfileRead,
    NutritionProgressCreate,
    NutritionProgressRead,
)
from app.services.nutrition import (
    create_meal_plan,
    create_nutrition_profile,
    create_nutrition_progress,
    get_nutrition_overview,
    list_meal_plans,
    list_nutrition_profiles,
    list_nutrition_progress_entries,
)


router = APIRouter()


@router.get("/overview", response_model=NutritionOverviewRead)
def read_nutrition_overview(_: CurrentUser, db: DbSession) -> NutritionOverviewRead:
    return NutritionOverviewRead.model_validate(get_nutrition_overview(db))


@router.get("/profiles", response_model=list[NutritionProfileRead])
def read_nutrition_profiles(
    _: CurrentUser,
    db: DbSession,
    member_id: UUID | None = None,
) -> list[NutritionProfileRead]:
    return [NutritionProfileRead.model_validate(item) for item in list_nutrition_profiles(db, member_id=member_id)]


@router.post("/profiles", response_model=NutritionProfileRead)
def create_nutrition_profile_record(
    payload: NutritionProfileCreate,
    _: CurrentUser,
    db: DbSession,
) -> NutritionProfileRead:
    return NutritionProfileRead.model_validate(create_nutrition_profile(db, payload))


@router.get("/meal-plans", response_model=list[MealPlanRead])
def read_meal_plans(
    _: CurrentUser,
    db: DbSession,
    nutrition_profile_id: UUID | None = None,
) -> list[MealPlanRead]:
    return [MealPlanRead.model_validate(item) for item in list_meal_plans(db, nutrition_profile_id=nutrition_profile_id)]


@router.post("/meal-plans", response_model=MealPlanRead)
def create_meal_plan_record(payload: MealPlanCreate, _: CurrentUser, db: DbSession) -> MealPlanRead:
    return MealPlanRead.model_validate(create_meal_plan(db, payload))


@router.get("/progress", response_model=list[NutritionProgressRead])
def read_nutrition_progress_entries(
    _: CurrentUser,
    db: DbSession,
    nutrition_profile_id: UUID | None = None,
) -> list[NutritionProgressRead]:
    return [
        NutritionProgressRead.model_validate(item)
        for item in list_nutrition_progress_entries(db, nutrition_profile_id=nutrition_profile_id)
    ]


@router.post("/progress", response_model=NutritionProgressRead)
def create_nutrition_progress_record(
    payload: NutritionProgressCreate,
    _: CurrentUser,
    db: DbSession,
) -> NutritionProgressRead:
    return NutritionProgressRead.model_validate(create_nutrition_progress(db, payload))