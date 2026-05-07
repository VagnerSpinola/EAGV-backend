from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NutritionOverviewRead(BaseModel):
    profile_count: int
    meal_plan_count: int
    progress_entry_count: int
    supplement_count: int
    lab_exam_count: int


class NutritionProfileCreate(BaseModel):
    member_id: UUID
    nutritionist_id: int = Field(gt=0)
    basal_metabolic_rate: Decimal | None = None
    daily_calorie_target: Decimal | None = None
    water_intake_goal: Decimal | None = None
    activity_level: str | None = Field(default=None, max_length=80)
    sleep_hours: Decimal | None = None
    stress_level: str | None = Field(default=None, max_length=80)
    primary_goal: str | None = Field(default=None, max_length=120)


class NutritionProfileRead(NutritionProfileCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MealPlanCreate(BaseModel):
    nutrition_profile_id: UUID
    title: str | None = Field(default=None, max_length=160)
    objective: str | None = None
    calories: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(default=None, max_length=50)


class MealPlanRead(MealPlanCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NutritionProgressCreate(BaseModel):
    nutrition_profile_id: UUID
    adherence_score: Decimal | None = None
    energy_level: str | None = Field(default=None, max_length=80)
    hunger_level: str | None = Field(default=None, max_length=80)
    mood: str | None = Field(default=None, max_length=80)
    notes: str | None = None
    recorded_at: datetime | None = None


class NutritionProgressRead(NutritionProgressCreate):
    id: UUID
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)