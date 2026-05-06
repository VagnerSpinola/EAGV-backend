from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.academy import CheckinType, MemberStatus, PaymentStatus


class MemberBase(BaseModel):
    plan_id: int | None = None
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
    plan_id: int | None = None
    status: MemberStatus


class MemberReportRead(BaseModel):
    id: UUID
    user_id: int
    full_name: str | None = None
    email: EmailStr
    is_active: bool
    plan_id: int | None = None
    plan_name: str | None = None
    plan_price: Decimal | None = None
    plan_duration_days: int | None = None
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


class ClassCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    frequency: int = Field(gt=0)
    plan_id: int = Field(gt=0)
    days: list[str] = Field(min_length=1)


class ClassRead(ClassCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    member_id: UUID
    amount: Decimal = Field(gt=0)
    method_id: int = Field(gt=0)


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
    notes: str | None = None


class MemberEnrollmentCreate(MemberCreate):
    body_measurement: BodyMeasurementInput | None = None


class BodyMeasurementRead(BodyMeasurementCreate):
    id: UUID
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)