from uuid import UUID

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.trainer import (
    ExerciseLibraryCreate,
    ExerciseLibraryRead,
    PhysicalAssessmentCreate,
    PhysicalAssessmentRead,
    TrainerOverviewRead,
    TrainerProfileCreate,
    TrainerProfileRead,
    TrainingSessionCreate,
    TrainingSessionRead,
    WorkoutPlanCreate,
    WorkoutPlanRead,
)
from app.services.trainer import (
    create_exercise_library_item,
    create_physical_assessment,
    create_trainer_profile,
    create_training_session,
    create_workout_plan,
    get_trainer_overview,
    list_exercise_library,
    list_physical_assessments,
    list_trainer_profiles,
    list_training_sessions,
    list_workout_plans,
)


router = APIRouter()


@router.get("/overview", response_model=TrainerOverviewRead)
def read_trainer_overview(_: CurrentUser, db: DbSession) -> TrainerOverviewRead:
    return TrainerOverviewRead.model_validate(get_trainer_overview(db))


@router.get("/profiles", response_model=list[TrainerProfileRead])
def read_trainer_profiles(_: CurrentUser, db: DbSession, user_id: int | None = None) -> list[TrainerProfileRead]:
    return [TrainerProfileRead.model_validate(item) for item in list_trainer_profiles(db, user_id=user_id)]


@router.post("/profiles", response_model=TrainerProfileRead)
def create_trainer_profile_record(payload: TrainerProfileCreate, _: CurrentUser, db: DbSession) -> TrainerProfileRead:
    return TrainerProfileRead.model_validate(create_trainer_profile(db, payload))


@router.get("/exercise-library", response_model=list[ExerciseLibraryRead])
def read_exercise_library(_: CurrentUser, db: DbSession) -> list[ExerciseLibraryRead]:
    return [ExerciseLibraryRead.model_validate(item) for item in list_exercise_library(db)]


@router.post("/exercise-library", response_model=ExerciseLibraryRead)
def create_exercise_library_record(
    payload: ExerciseLibraryCreate,
    _: CurrentUser,
    db: DbSession,
) -> ExerciseLibraryRead:
    return ExerciseLibraryRead.model_validate(create_exercise_library_item(db, payload))


@router.get("/workout-plans", response_model=list[WorkoutPlanRead])
def read_workout_plans(
    _: CurrentUser,
    db: DbSession,
    member_id: UUID | None = None,
    trainer_id: int | None = None,
) -> list[WorkoutPlanRead]:
    return [WorkoutPlanRead.model_validate(item) for item in list_workout_plans(db, member_id=member_id, trainer_id=trainer_id)]


@router.post("/workout-plans", response_model=WorkoutPlanRead)
def create_workout_plan_record(payload: WorkoutPlanCreate, _: CurrentUser, db: DbSession) -> WorkoutPlanRead:
    return WorkoutPlanRead.model_validate(create_workout_plan(db, payload))


@router.get("/training-sessions", response_model=list[TrainingSessionRead])
def read_training_sessions(
    _: CurrentUser,
    db: DbSession,
    member_id: UUID | None = None,
    trainer_id: int | None = None,
) -> list[TrainingSessionRead]:
    return [
        TrainingSessionRead.model_validate(item)
        for item in list_training_sessions(db, member_id=member_id, trainer_id=trainer_id)
    ]


@router.post("/training-sessions", response_model=TrainingSessionRead)
def create_training_session_record(
    payload: TrainingSessionCreate,
    _: CurrentUser,
    db: DbSession,
) -> TrainingSessionRead:
    return TrainingSessionRead.model_validate(create_training_session(db, payload))


@router.get("/physical-assessments", response_model=list[PhysicalAssessmentRead])
def read_physical_assessments(
    _: CurrentUser,
    db: DbSession,
    member_id: UUID | None = None,
    trainer_id: int | None = None,
) -> list[PhysicalAssessmentRead]:
    return [
        PhysicalAssessmentRead.model_validate(item)
        for item in list_physical_assessments(db, member_id=member_id, trainer_id=trainer_id)
    ]


@router.post("/physical-assessments", response_model=PhysicalAssessmentRead)
def create_physical_assessment_record(
    payload: PhysicalAssessmentCreate,
    _: CurrentUser,
    db: DbSession,
) -> PhysicalAssessmentRead:
    return PhysicalAssessmentRead.model_validate(create_physical_assessment(db, payload))