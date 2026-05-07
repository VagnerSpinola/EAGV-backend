from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TrainerProfile(Base):
    __tablename__ = "trainer_profiles"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cref_registration: Mapped[str | None] = mapped_column(String(80), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_years: Mapped[int | None] = mapped_column(nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ExerciseLibrary(Base):
    __tablename__ = "exercise_library"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    muscle_group: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    exercise_type: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    equipment: Mapped[str | None] = mapped_column(String(120), nullable=True)
    difficulty_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class WorkoutDay(Base):
    __tablename__ = "workout_days"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    workout_plan_id: Mapped[UUID] = mapped_column(ForeignKey("workout_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    day_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    focus_area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    workout_day_id: Mapped[UUID] = mapped_column(ForeignKey("workout_days.id", ondelete="CASCADE"), index=True, nullable=False)
    exercise_id: Mapped[UUID] = mapped_column(ForeignKey("exercise_library.id", ondelete="RESTRICT"), index=True, nullable=False)
    exercise_order: Mapped[int | None] = mapped_column(nullable=True)
    sets: Mapped[int | None] = mapped_column(nullable=True)
    reps: Mapped[str | None] = mapped_column(String(80), nullable=True)
    rest_seconds: Mapped[int | None] = mapped_column(nullable=True)
    tempo: Mapped[str | None] = mapped_column(String(40), nullable=True)
    load_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    observation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class MemberWorkoutHistory(Base):
    __tablename__ = "member_workout_history"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    workout_plan_id: Mapped[UUID] = mapped_column(ForeignKey("workout_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    calories_burned: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    perceived_effort: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class TrainerNote(Base):
    __tablename__ = "trainer_notes"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    note_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class TrainingGoal(Base):
    __tablename__ = "training_goals"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    goal_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    target_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    current_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    session_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    location: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class TrainingAttendance(Base):
    __tablename__ = "training_attendance"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    training_session_id: Mapped[UUID] = mapped_column(ForeignKey("training_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    attendance_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    check_in_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ExerciseProgress(Base):
    __tablename__ = "exercise_progress"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    exercise_id: Mapped[UUID] = mapped_column(ForeignKey("exercise_library.id", ondelete="CASCADE"), index=True, nullable=False)
    max_weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    repetitions: Mapped[int | None] = mapped_column(nullable=True)
    execution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class WorkoutPeriodization(Base):
    __tablename__ = "workout_periodization"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    workout_plan_id: Mapped[UUID] = mapped_column(ForeignKey("workout_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    phase_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    intensity_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    volume_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )