from datetime import date, datetime, time, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Time, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class NutritionProfile(Base):
    __tablename__ = "nutrition_profiles"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    nutritionist_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    basal_metabolic_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    daily_calorie_target: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    water_intake_goal: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    activity_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sleep_hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    stress_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    primary_goal: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class NutritionAnamnesis(Base):
    __tablename__ = "nutrition_anamnesis"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    nutrition_profile_id: Mapped[UUID] = mapped_column(ForeignKey("nutrition_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    meals_per_day: Mapped[int | None] = mapped_column(nullable=True)
    alcohol_consumption: Mapped[str | None] = mapped_column(String(80), nullable=True)
    smoking: Mapped[bool | None] = mapped_column(nullable=True)
    water_intake: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    digestive_issues: Mapped[str | None] = mapped_column(Text, nullable=True)
    food_cravings: Mapped[str | None] = mapped_column(Text, nullable=True)
    wake_up_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    sleep_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    work_routine: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_diets: Mapped[str | None] = mapped_column(Text, nullable=True)
    eating_disorders_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class FoodRestriction(Base):
    __tablename__ = "food_restrictions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    nutrition_profile_id: Mapped[UUID] = mapped_column(ForeignKey("nutrition_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    restriction_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class NutritionGoal(Base):
    __tablename__ = "nutrition_goals"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    nutrition_profile_id: Mapped[UUID] = mapped_column(ForeignKey("nutrition_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    goal_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    target_body_fat: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    nutrition_profile_id: Mapped[UUID] = mapped_column(ForeignKey("nutrition_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    calories: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class MealPlanMeal(Base):
    __tablename__ = "meal_plan_meals"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    meal_plan_id: Mapped[UUID] = mapped_column(ForeignKey("meal_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    meal_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    time: Mapped[time | None] = mapped_column(Time, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class MealFood(Base):
    __tablename__ = "meal_foods"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    meal_id: Mapped[UUID] = mapped_column(ForeignKey("meal_plan_meals.id", ondelete="CASCADE"), index=True, nullable=False)
    food_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    calories: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    protein: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    carbs: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    fat: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Supplement(Base):
    __tablename__ = "supplements"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    nutrition_profile_id: Mapped[UUID] = mapped_column(ForeignKey("nutrition_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    supplement_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    dosage: Mapped[str | None] = mapped_column(String(120), nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(120), nullable=True)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class LabExam(Base):
    __tablename__ = "lab_exams"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    nutrition_profile_id: Mapped[UUID] = mapped_column(ForeignKey("nutrition_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    exam_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class NutritionProgress(Base):
    __tablename__ = "nutrition_progress"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    nutrition_profile_id: Mapped[UUID] = mapped_column(ForeignKey("nutrition_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    adherence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    energy_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    hunger_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    mood: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )