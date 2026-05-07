from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TrainerOverviewRead(BaseModel):
    trainer_profile_count: int
    exercise_library_count: int
    workout_plan_count: int
    training_session_count: int
    physical_assessment_count: int
    training_goal_count: int
    exercise_progress_count: int


class TrainerProfileCreate(BaseModel):
    user_id: int = Field(gt=0)
    specialty: str | None = Field(default=None, max_length=120)
    cref_registration: str | None = Field(default=None, max_length=80)
    bio: str | None = None
    experience_years: int | None = Field(default=None, ge=0)
    instagram_url: str | None = None
    profile_photo_url: str | None = None


class TrainerProfileRead(TrainerProfileCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseLibraryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    muscle_group: str | None = Field(default=None, max_length=120)
    exercise_type: str | None = Field(default=None, max_length=80)
    equipment: str | None = Field(default=None, max_length=120)
    difficulty_level: str | None = Field(default=None, max_length=80)
    instructions: str | None = None
    video_url: str | None = None
    image_url: str | None = None
    created_by: int | None = Field(default=None, gt=0)


class ExerciseLibraryRead(ExerciseLibraryCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanCreate(BaseModel):
    member_id: UUID
    trainer_id: int = Field(gt=0)
    title: str | None = Field(default=None, max_length=160)
    objective: str | None = None
    difficulty_level: str | None = Field(default=None, max_length=80)
    status: str | None = Field(default=None, max_length=50)
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class WorkoutPlanRead(WorkoutPlanCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainingSessionCreate(BaseModel):
    trainer_id: int = Field(gt=0)
    member_id: UUID
    scheduled_start: datetime
    scheduled_end: datetime | None = None
    session_type: str | None = Field(default=None, max_length=80)
    location: str | None = Field(default=None, max_length=160)
    notes: str | None = None
    status: str | None = Field(default=None, max_length=50)


class TrainingSessionRead(TrainingSessionCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PhysicalAssessmentCreate(BaseModel):
    member_id: UUID
    trainer_id: int | None = Field(default=None, gt=0)
    body_measurement_id: UUID | None = None
    vo2_estimate: Decimal | None = None
    resting_heart_rate: int | None = None
    flexibility_score: Decimal | None = None
    strength_score: Decimal | None = None
    posture_notes: str | None = None
    posture_analysis: str | None = None
    mobility_score: Decimal | None = None
    cardio_conditioning: str | None = None
    injury_history: str | None = None
    limitations: str | None = None
    recommendations: str | None = None
    assessment_date: datetime | None = None


class PhysicalAssessmentRead(PhysicalAssessmentCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)