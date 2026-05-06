from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from fastapi import UploadFile

from app.models.academy import BodyMeasurement, Checkin, Member, MemberStatus, Payment, PaymentMethod, PaymentStatus, Plan
from app.models.user import User, UserRole
from app.schemas.academy import (
    BodyMeasurementCreate,
    BodyMeasurementInput,
    CheckinCreate,
    MemberCreate,
    MemberEnrollmentCreate,
    PaymentCreate,
    PaymentMethodCreate,
    PlanCreate,
)
from app.schemas.user import UserCreate
from app.services.auth import create_user
from app.services.user_images import delete_user_image_by_url, upload_user_image as upload_member_image


def list_member_summaries(db: Session) -> list[dict[str, object]]:
    rows = db.execute(
        select(Member, User)
        .join(User, User.id == Member.user_id)
        .order_by(User.full_name.asc(), User.email.asc())
    ).all()
    return [
        {
            "id": member.id,
            "user_id": member.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "cpf": member.cpf,
            "phone": member.phone,
            "plan_id": member.plan_id,
            "status": member.status,
        }
        for member, user in rows
    ]


def get_member_by_id(db: Session, member_id) -> Member | None:
    return db.execute(select(Member).where(Member.id == member_id)).scalar_one_or_none()


def _validate_member_dependencies(db: Session, member_in: MemberCreate) -> None:
    existing_member = db.execute(select(Member).where(Member.cpf == member_in.cpf)).scalar_one_or_none()
    if existing_member is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A member with this CPF already exists.")

    if member_in.plan_id is not None:
        selected_plan = db.execute(select(Plan).where(Plan.id == member_in.plan_id)).scalar_one_or_none()
        if selected_plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Selected plan not found.")


def _build_body_measurement(member_id, body_measurement_in: BodyMeasurementInput, *, created_by: int) -> BodyMeasurement:
    return BodyMeasurement(
        member_id=member_id,
        recorded_at=body_measurement_in.recorded_at,
        weight=body_measurement_in.weight,
        height=body_measurement_in.height,
        body_fat_percentage=body_measurement_in.body_fat_percentage,
        muscle_mass=body_measurement_in.muscle_mass,
        chest=body_measurement_in.chest,
        waist=body_measurement_in.waist,
        hips=body_measurement_in.hips,
        arm_left=body_measurement_in.arm_left,
        arm_right=body_measurement_in.arm_right,
        thigh_left=body_measurement_in.thigh_left,
        thigh_right=body_measurement_in.thigh_right,
        calf_left=body_measurement_in.calf_left,
        calf_right=body_measurement_in.calf_right,
        notes=body_measurement_in.notes,
        created_by=created_by,
    )


def create_member(db: Session, member_in: MemberCreate, *, photo_file: UploadFile | None = None) -> Member:
    _validate_member_dependencies(db, member_in)

    uploaded_photo_url: str | None = None
    try:
        user = create_user(
            db,
            UserCreate(
                email=member_in.email,
                full_name=member_in.full_name,
                image_url=None,
                role=UserRole.CLIENT,
                sector=None,
                password=member_in.password,
            ),
            auto_commit=False,
        )

        photo_url = member_in.photo_url
        if photo_file is not None:
            uploaded_photo_url = upload_member_image(file=photo_file, user_id=user.id)
            photo_url = uploaded_photo_url
            user.image_url = photo_url
            db.add(user)

        member = Member(
            user_id=user.id,
            plan_id=member_in.plan_id,
            cpf=member_in.cpf,
            birth_date=member_in.birth_date,
            phone=member_in.phone,
            gender=member_in.gender,
            photo_url=photo_url,
            street=member_in.street,
            number=member_in.number,
            city=member_in.city,
            state=member_in.state,
            country=member_in.country,
            zip_code=member_in.zip_code,
            status=member_in.status,
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    except Exception:
        db.rollback()
        if uploaded_photo_url:
            delete_user_image_by_url(uploaded_photo_url)
        raise


def create_member_enrollment(
    db: Session,
    enrollment_in: MemberEnrollmentCreate,
    *,
    created_by: int,
    photo_file: UploadFile | None = None,
) -> Member:
    _validate_member_dependencies(db, enrollment_in)

    uploaded_photo_url: str | None = None
    try:
        user = create_user(
            db,
            UserCreate(
                email=enrollment_in.email,
                full_name=enrollment_in.full_name,
                image_url=None,
                role=UserRole.CLIENT,
                sector=None,
                password=enrollment_in.password,
            ),
            auto_commit=False,
        )

        photo_url = enrollment_in.photo_url
        if photo_file is not None:
            uploaded_photo_url = upload_member_image(file=photo_file, user_id=user.id)
            photo_url = uploaded_photo_url
            user.image_url = photo_url
            db.add(user)

        member = Member(
            user_id=user.id,
            plan_id=enrollment_in.plan_id,
            cpf=enrollment_in.cpf,
            birth_date=enrollment_in.birth_date,
            phone=enrollment_in.phone,
            gender=enrollment_in.gender,
            photo_url=photo_url,
            street=enrollment_in.street,
            number=enrollment_in.number,
            city=enrollment_in.city,
            state=enrollment_in.state,
            country=enrollment_in.country,
            zip_code=enrollment_in.zip_code,
            status=enrollment_in.status,
        )
        db.add(member)
        db.flush()

        if enrollment_in.body_measurement is not None:
            db.add(_build_body_measurement(member.id, enrollment_in.body_measurement, created_by=created_by))

        db.commit()
        db.refresh(member)
        return member
    except Exception:
        db.rollback()
        if uploaded_photo_url:
            delete_user_image_by_url(uploaded_photo_url)
        raise


def list_plans(db: Session) -> list[Plan]:
    return db.execute(select(Plan).order_by(Plan.name.asc())).scalars().all()


def create_plan(db: Session, plan_in: PlanCreate) -> Plan:
    existing_plan = db.execute(select(Plan).where(Plan.name == plan_in.name)).scalar_one_or_none()
    if existing_plan is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A plan with this name already exists.")

    plan = Plan(**plan_in.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def list_payment_methods(db: Session) -> list[PaymentMethod]:
    return db.execute(select(PaymentMethod).order_by(PaymentMethod.description.asc())).scalars().all()


def create_payment_method(db: Session, payment_method_in: PaymentMethodCreate) -> PaymentMethod:
    existing_payment_method_by_description = db.execute(
        select(PaymentMethod).where(PaymentMethod.description == payment_method_in.description)
    ).scalar_one_or_none()
    if existing_payment_method_by_description is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A payment method with this description already exists.")

    payment_method = PaymentMethod(description=payment_method_in.description)
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    return payment_method


def _build_payment_read(payment: Payment, payment_method: PaymentMethod) -> dict[str, object]:
    return {
        "id": payment.id,
        "member_id": payment.member_id,
        "amount": payment.amount,
        "method_id": payment.method_id,
        "method_description": payment_method.description,
        "status": payment.status,
        "created_at": payment.created_at,
    }


def list_payments(db: Session) -> list[dict[str, object]]:
    rows = db.execute(
        select(Payment, PaymentMethod)
        .join(PaymentMethod, PaymentMethod.id == Payment.method_id)
        .order_by(Payment.created_at.desc())
    ).all()
    return [_build_payment_read(payment, payment_method) for payment, payment_method in rows]


def list_member_payment_history(db: Session, member_id: UUID) -> list[dict[str, object]]:
    member = get_member_by_id(db, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    reference_now = datetime.now(timezone.utc)
    history_start = datetime(reference_now.year, 1, 1, tzinfo=timezone.utc)
    if reference_now.month == 1:
        history_start = datetime(reference_now.year - 1, 10, 1, tzinfo=timezone.utc)

    rows = db.execute(
        select(Payment, PaymentMethod)
        .join(PaymentMethod, PaymentMethod.id == Payment.method_id)
        .where(Payment.member_id == member_id, Payment.created_at >= history_start)
        .order_by(Payment.created_at.desc())
    ).all()
    return [_build_payment_read(payment, payment_method) for payment, payment_method in rows]


def create_payment(db: Session, payment_in: PaymentCreate) -> dict[str, object]:
    member = get_member_by_id(db, payment_in.member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    user = db.execute(select(User).where(User.id == member.user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for the selected member.")

    payment_method = db.execute(
        select(PaymentMethod).where(PaymentMethod.id == payment_in.method_id)
    ).scalar_one_or_none()
    if payment_method is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found.")

    payment = Payment(
        member_id=payment_in.member_id,
        amount=payment_in.amount,
        method_id=payment_in.method_id,
        status=PaymentStatus.SUCCESS,
        idempotency_key=f"pay-{uuid4().hex}",
    )

    user.is_active = True
    member.status = MemberStatus.ACTIVE
    db.add(user)
    db.add(member)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return _build_payment_read(payment, payment_method)


def list_checkins(db: Session) -> list[Checkin]:
    return db.execute(select(Checkin).order_by(Checkin.checkin_datetime.desc())).scalars().all()


def create_checkin(db: Session, checkin_in: CheckinCreate) -> Checkin:
    member = get_member_by_id(db, checkin_in.member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    payload = checkin_in.model_dump(exclude_none=True)
    checkin = Checkin(**payload)
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


def list_body_measurements(db: Session) -> list[BodyMeasurement]:
    return db.execute(select(BodyMeasurement).order_by(BodyMeasurement.recorded_at.desc())).scalars().all()


def create_body_measurement(
    db: Session,
    body_measurement_in: BodyMeasurementCreate,
    *,
    created_by: int,
) -> BodyMeasurement:
    member = get_member_by_id(db, body_measurement_in.member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    body_measurement = BodyMeasurement(**body_measurement_in.model_dump(), created_by=created_by)
    db.add(body_measurement)
    db.commit()
    db.refresh(body_measurement)
    return body_measurement