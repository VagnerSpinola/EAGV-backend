from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.academy import BodyMeasurement, Member, PhysicalAssessment
from app.models.trainer import ExerciseLibrary, ExerciseProgress, TrainerProfile, TrainingGoal, TrainingSession, WorkoutPlan
from app.models.user import User
from app.schemas.trainer import (
    ExerciseLibraryCreate,
    PhysicalAssessmentCreate,
    TrainerProfileCreate,
    TrainingSessionCreate,
    WorkoutPlanCreate,
)


def _ensure_member_exists(db: Session, member_id: UUID) -> None:
    if db.get(Member, member_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")


def _ensure_user_exists(db: Session, user_id: int) -> None:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")


def _ensure_body_measurement_exists(db: Session, measurement_id: UUID | None) -> None:
    if measurement_id is None:
        return

    if db.get(BodyMeasurement, measurement_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Body measurement not found.")


def list_trainer_profiles(db: Session, *, user_id: int | None = None) -> list[TrainerProfile]:
    statement = select(TrainerProfile)
    if user_id is not None:
        statement = statement.where(TrainerProfile.user_id == user_id)

    return db.execute(statement.order_by(TrainerProfile.created_at.desc())).scalars().all()


def create_trainer_profile(db: Session, payload: TrainerProfileCreate) -> TrainerProfile:
    _ensure_user_exists(db, payload.user_id)

    profile = TrainerProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def list_exercise_library(db: Session) -> list[ExerciseLibrary]:
    return db.execute(select(ExerciseLibrary).order_by(ExerciseLibrary.name.asc())).scalars().all()


def create_exercise_library_item(db: Session, payload: ExerciseLibraryCreate) -> ExerciseLibrary:
    if payload.created_by is not None:
        _ensure_user_exists(db, payload.created_by)

    exercise = ExerciseLibrary(**payload.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


def list_workout_plans(
    db: Session,
    *,
    member_id: UUID | None = None,
    trainer_id: int | None = None,
) -> list[WorkoutPlan]:
    statement = select(WorkoutPlan)
    if member_id is not None:
        statement = statement.where(WorkoutPlan.member_id == member_id)
    if trainer_id is not None:
        statement = statement.where(WorkoutPlan.trainer_id == trainer_id)

    return db.execute(statement.order_by(WorkoutPlan.created_at.desc())).scalars().all()


def create_workout_plan(db: Session, payload: WorkoutPlanCreate) -> WorkoutPlan:
    _ensure_member_exists(db, payload.member_id)
    _ensure_user_exists(db, payload.trainer_id)

    workout_plan = WorkoutPlan(**payload.model_dump())
    db.add(workout_plan)
    db.commit()
    db.refresh(workout_plan)
    return workout_plan


def list_training_sessions(
    db: Session,
    *,
    member_id: UUID | None = None,
    trainer_id: int | None = None,
) -> list[TrainingSession]:
    statement = select(TrainingSession)
    if member_id is not None:
        statement = statement.where(TrainingSession.member_id == member_id)
    if trainer_id is not None:
        statement = statement.where(TrainingSession.trainer_id == trainer_id)

    return db.execute(statement.order_by(TrainingSession.scheduled_start.desc())).scalars().all()


def create_training_session(db: Session, payload: TrainingSessionCreate) -> TrainingSession:
    _ensure_member_exists(db, payload.member_id)
    _ensure_user_exists(db, payload.trainer_id)

    training_session = TrainingSession(**payload.model_dump())
    db.add(training_session)
    db.commit()
    db.refresh(training_session)
    return training_session


def list_physical_assessments(
    db: Session,
    *,
    member_id: UUID | None = None,
    trainer_id: int | None = None,
) -> list[PhysicalAssessment]:
    statement = select(PhysicalAssessment)
    if member_id is not None:
        statement = statement.where(PhysicalAssessment.member_id == member_id)
    if trainer_id is not None:
        statement = statement.where(PhysicalAssessment.trainer_id == trainer_id)

    return db.execute(statement.order_by(PhysicalAssessment.assessment_date.desc(), PhysicalAssessment.id.desc())).scalars().all()


def create_physical_assessment(db: Session, payload: PhysicalAssessmentCreate) -> PhysicalAssessment:
    _ensure_member_exists(db, payload.member_id)
    if payload.trainer_id is not None:
        _ensure_user_exists(db, payload.trainer_id)
    _ensure_body_measurement_exists(db, payload.body_measurement_id)

    assessment_payload = payload.model_dump()
    if assessment_payload["assessment_date"] is None:
        assessment_payload["assessment_date"] = datetime.now(timezone.utc)
    if assessment_payload["posture_analysis"] is None and assessment_payload["posture_notes"] is not None:
        assessment_payload["posture_analysis"] = assessment_payload["posture_notes"]

    assessment = PhysicalAssessment(**assessment_payload)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_trainer_overview(db: Session) -> dict[str, int]:
    return {
        "trainer_profile_count": db.scalar(select(func.count()).select_from(TrainerProfile)) or 0,
        "exercise_library_count": db.scalar(select(func.count()).select_from(ExerciseLibrary)) or 0,
        "workout_plan_count": db.scalar(select(func.count()).select_from(WorkoutPlan)) or 0,
        "training_session_count": db.scalar(select(func.count()).select_from(TrainingSession)) or 0,
        "physical_assessment_count": db.scalar(select(func.count()).select_from(PhysicalAssessment)) or 0,
        "training_goal_count": db.scalar(select(func.count()).select_from(TrainingGoal)) or 0,
        "exercise_progress_count": db.scalar(select(func.count()).select_from(ExerciseProgress)) or 0,
    }