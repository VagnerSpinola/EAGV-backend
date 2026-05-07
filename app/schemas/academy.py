from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.academy import CheckinType, MemberStatus, PaymentStatus


class MemberBase(BaseModel):
    cpf: str = Field(min_length=11, max_length=14)
    birth_date: date
    phone: str = Field(min_length=8, max_length=30)
    gender: str = Field(min_length=1, max_length=30)
    photo_url: str | None = Field(default=None, max_length=500)
    street: str = Field(min_length=1, max_length=255)
    number: str = Field(min_length=1, max_length=30)
    city: str = Field(default="Tabapua", max_length=100)
    state: str = Field(default="Sao Paulo", max_length=100)
    country: str = Field(default="Brasil", max_length=100)
    zip_code: str = Field(min_length=5, max_length=20)
    status: MemberStatus = MemberStatus.ACTIVE


class MemberCreate(MemberBase):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class MemberRead(MemberBase):
    id: UUID
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberSummaryRead(BaseModel):
    id: UUID
    user_id: int
    full_name: str | None = None
    email: EmailStr
    cpf: str
    phone: str
    assigned_class_count: int = 0
    assigned_plan_names: list[str] = Field(default_factory=list)
    status: MemberStatus


class MemberReportRead(BaseModel):
    id: UUID
    user_id: int
    full_name: str | None = None
    email: EmailStr
    is_active: bool
    assigned_class_titles: list[str] = Field(default_factory=list)
    assigned_plan_names: list[str] = Field(default_factory=list)
    cpf: str
    birth_date: date
    phone: str
    gender: str
    photo_url: str | None = None
    street: str
    number: str
    city: str
    state: str
    country: str
    zip_code: str
    status: MemberStatus
    created_at: datetime
    updated_at: datetime


class PaymentMethodRead(BaseModel):
    id: int
    description: str

    model_config = ConfigDict(from_attributes=True)


class PaymentMethodCreate(BaseModel):
    description: str = Field(min_length=1, max_length=120)


class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    price: Decimal = Field(gt=0)
    duration_days: int = Field(gt=0)


class PlanRead(PlanCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


ClassDay = Literal["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]


class ClassScheduleInput(BaseModel):
    day: ClassDay
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_time_range(self) -> "ClassScheduleInput":
        if self.end_time <= self.start_time:
            raise ValueError("Class end_time must be later than start_time.")

        return self


class ClassCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    frequency: int = Field(gt=0)
    plan_id: int = Field(gt=0)
    schedules: list[ClassScheduleInput] = Field(min_length=1)


class ClassRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    frequency: int
    plan_id: int
    days: list[ClassDay]
    schedules: list[ClassScheduleInput]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberClassAssignmentWrite(BaseModel):
    class_ids: list[int] = Field(default_factory=list)


class MemberClassAssignmentItemRead(BaseModel):
    assignment_id: int
    class_id: int
    title: str
    description: str | None = None
    frequency: int
    plan_id: int
    days: list[ClassDay]
    schedules: list[ClassScheduleInput]
    assigned_by: int
    assigned_at: datetime


class MemberClassAssignmentsRead(BaseModel):
    member_id: UUID
    classes: list[MemberClassAssignmentItemRead]


class PaymentCreate(BaseModel):
    member_id: UUID
    amount: Decimal = Field(gt=0)
    method_id: int = Field(gt=0)
    class_ids: list[int] = Field(min_length=1)


class PaymentRead(BaseModel):
    id: int
    member_id: UUID
    amount: Decimal
    method_id: int
    operator_id: int
    method_description: str
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckinCreate(BaseModel):
    member_id: UUID
    checkin_datetime: datetime | None = None
    checkout_datetime: datetime | None = None
    type: CheckinType


class CheckinRead(BaseModel):
    id: int
    member_id: UUID
    checkin_datetime: datetime
    checkout_datetime: datetime | None
    type: CheckinType

    model_config = ConfigDict(from_attributes=True)


CheckinPaymentCoverageStatus = Literal["paid", "expired", "payment_required"]


class CheckinPaymentStatusClassRead(BaseModel):
    class_id: int
    title: str
    plan_id: int
    plan_name: str
    plan_price: Decimal
    plan_duration_days: int
    status: CheckinPaymentCoverageStatus
    last_payment_id: int | None = None
    last_payment_at: datetime | None = None
    paid_from: datetime | None = None
    paid_until: datetime | None = None


class CheckinPaymentStatusSummaryRead(BaseModel):
    assigned_class_count: int
    paid_class_count: int
    expired_class_count: int
    pending_class_count: int
    total_assigned_amount: Decimal
    total_pending_amount: Decimal


class CheckinPaymentStatusRead(BaseModel):
    message: str
    member_id: UUID
    classes: list[CheckinPaymentStatusClassRead] = Field(default_factory=list)
    summary: CheckinPaymentStatusSummaryRead


class BodyMeasurementCreate(BaseModel):
    member_id: UUID
    recorded_at: datetime
    weight: Decimal | None = None
    height: Decimal | None = None
    body_fat_percentage: Decimal | None = None
    muscle_mass: Decimal | None = None
    chest: Decimal | None = None
    waist: Decimal | None = None
    hips: Decimal | None = None
    arm_left: Decimal | None = None
    arm_right: Decimal | None = None
    thigh_left: Decimal | None = None
    thigh_right: Decimal | None = None
    calf_left: Decimal | None = None
    calf_right: Decimal | None = None
    visceral_fat: Decimal | None = None
    bmi: Decimal | None = None
    notes: str | None = None


class BodyMeasurementInput(BaseModel):
    recorded_at: datetime
    weight: Decimal | None = None
    height: Decimal | None = None
    body_fat_percentage: Decimal | None = None
    muscle_mass: Decimal | None = None
    chest: Decimal | None = None
    waist: Decimal | None = None
    hips: Decimal | None = None
    arm_left: Decimal | None = None
    arm_right: Decimal | None = None
    thigh_left: Decimal | None = None
    thigh_right: Decimal | None = None
    calf_left: Decimal | None = None
    calf_right: Decimal | None = None
    visceral_fat: Decimal | None = None
    bmi: Decimal | None = None
    notes: str | None = None


class MemberEnrollmentCreate(MemberCreate):
    body_measurement: BodyMeasurementInput | None = None


class BodyMeasurementRead(BodyMeasurementCreate):
    id: UUID
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)