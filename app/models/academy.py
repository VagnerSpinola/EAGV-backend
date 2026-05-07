from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _enum_values(enum_class: type[StrEnum]) -> list[str]:
    return [item.value for item in enum_class]


class MemberStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class PaymentStatus(StrEnum):
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"
    CANCELED = "canceled"


class CheckinType(StrEnum):
    GYM = "gym"
    POOL = "pool"
    COURT = "court"


class BodyPhotoType(StrEnum):
    FRONT = "front"
    SIDE = "side"
    BACK = "back"


class Member(Base):
    __tablename__ = "members"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    cpf: Mapped[str] = mapped_column(String(14), unique=True, index=True, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    gender: Mapped[str] = mapped_column(String(30), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    number: Mapped[str] = mapped_column(String(30), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, default="Tabapua", server_default="Tabapua")
    state: Mapped[str] = mapped_column(String(100), nullable=False, default="Sao Paulo", server_default="Sao Paulo")
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Brasil", server_default="Brasil")
    zip_code: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[MemberStatus] = mapped_column(
        Enum(MemberStatus, name="member_status", native_enum=False, values_callable=_enum_values),
        nullable=False,
        default=MemberStatus.ACTIVE,
        server_default=MemberStatus.ACTIVE.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    duration_days: Mapped[int] = mapped_column(nullable=False)


class AcademyClass(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency: Mapped[int] = mapped_column(nullable=False)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id", ondelete="RESTRICT"), index=True, nullable=False)
    days: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    schedules: Mapped[list[dict[str, str | None]]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class MemberClassAssignment(Base):
    __tablename__ = "member_class_assignments"
    __table_args__ = (UniqueConstraint("member_id", "class_id", name="uq_member_class_assignments_member_class"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"), index=True, nullable=False)
    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    method_id: Mapped[int] = mapped_column(ForeignKey("payment_methods.id", ondelete="RESTRICT"), index=True, nullable=False)
    operator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status", native_enum=False, values_callable=_enum_values),
        nullable=False,
        default=PaymentStatus.SUCCESS,
        server_default=PaymentStatus.SUCCESS.value,
    )
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class PaymentClassCoverage(Base):
    __tablename__ = "payment_class_coverages"
    __table_args__ = (UniqueConstraint("payment_id", "class_id", name="uq_payment_class_coverages_payment_class"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id", ondelete="CASCADE"), index=True, nullable=False)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id", ondelete="RESTRICT"), index=True, nullable=False)
    class_title_snapshot: Mapped[str] = mapped_column(String(160), nullable=False)
    plan_id_snapshot: Mapped[int] = mapped_column(nullable=False)
    plan_name_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    plan_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    plan_duration_days_snapshot: Mapped[int] = mapped_column(nullable=False)
    covered_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    covered_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Checkin(Base):
    __tablename__ = "checkins"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    checkin_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    checkout_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    type: Mapped[CheckinType] = mapped_column(
        Enum(CheckinType, name="checkin_type", native_enum=False, values_callable=_enum_values),
        nullable=False,
    )


class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    height: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    body_fat_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    muscle_mass: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    chest: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    waist: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    hips: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    arm_left: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    arm_right: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    thigh_left: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    thigh_right: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    calf_left: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    calf_right: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    visceral_fat: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    bmi: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class BodyPhoto(Base):
    __tablename__ = "body_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    front_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    side_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    back_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    taken_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    type: Mapped[BodyPhotoType] = mapped_column(
        Enum(BodyPhotoType, name="body_photo_type", native_enum=False, values_callable=_enum_values),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class PhysicalAssessment(Base):
    __tablename__ = "physical_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True, nullable=False)
    trainer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=True)
    body_measurement_id: Mapped[UUID | None] = mapped_column(ForeignKey("body_measurements.id", ondelete="SET NULL"), nullable=True)
    vo2_estimate: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    resting_heart_rate: Mapped[int | None] = mapped_column(nullable=True)
    flexibility_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    strength_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    posture_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    posture_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    mobility_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    cardio_conditioning: Mapped[str | None] = mapped_column(Text, nullable=True)
    injury_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    limitations: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessment_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )