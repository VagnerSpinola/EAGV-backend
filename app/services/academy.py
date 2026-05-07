from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from fastapi import UploadFile

from app.models.academy import AcademyClass, BodyMeasurement, Checkin, Member, MemberClassAssignment, MemberStatus, Payment, PaymentClassCoverage, PaymentMethod, PaymentStatus, Plan
from app.models.user import User, UserRole
from app.schemas.academy import (
    BodyMeasurementCreate,
    BodyMeasurementInput,
    ClassCreate,
    CheckinCreate,
    MemberCreate,
    MemberClassAssignmentWrite,
    MemberEnrollmentCreate,
    PaymentCreate,
    PaymentMethodCreate,
    PlanCreate,
)
from app.schemas.user import UserCreate
from app.services.auth import create_user
from app.services.user_images import delete_user_image_by_url, upload_user_image as upload_member_image


def _build_member_assignment_map(db: Session, member_ids: list[UUID]) -> dict[UUID, dict[str, list[str]]]:
    if not member_ids:
        return {}

    assignment_map: dict[UUID, dict[str, list[str]]] = {
        member_id: {"class_titles": [], "plan_names": []}
        for member_id in member_ids
    }
    rows = db.execute(
        select(MemberClassAssignment.member_id, AcademyClass.title, Plan.name)
        .join(AcademyClass, AcademyClass.id == MemberClassAssignment.class_id)
        .join(Plan, Plan.id == AcademyClass.plan_id)
        .where(MemberClassAssignment.member_id.in_(member_ids))
        .order_by(MemberClassAssignment.member_id.asc(), AcademyClass.title.asc(), Plan.name.asc())
    ).all()

    for member_id, class_title, plan_name in rows:
        details = assignment_map.setdefault(member_id, {"class_titles": [], "plan_names": []})
        if class_title not in details["class_titles"]:
            details["class_titles"].append(class_title)
        if plan_name not in details["plan_names"]:
            details["plan_names"].append(plan_name)

    return assignment_map


def _format_decimal_amount(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def _list_member_billing_assignments(db: Session, member_id: UUID) -> list[dict[str, object]]:
    rows = db.execute(
        select(AcademyClass.id, AcademyClass.title, Plan.id, Plan.name, Plan.price, Plan.duration_days)
        .join(MemberClassAssignment, MemberClassAssignment.class_id == AcademyClass.id)
        .join(Plan, Plan.id == AcademyClass.plan_id)
        .where(MemberClassAssignment.member_id == member_id)
        .order_by(AcademyClass.title.asc(), AcademyClass.id.asc())
    ).all()

    return [
        {
            "class_id": class_id,
            "class_title": class_title,
            "plan_id": plan_id,
            "plan_name": plan_name,
            "plan_price": plan_price,
            "plan_duration_days": plan_duration_days,
        }
        for class_id, class_title, plan_id, plan_name, plan_price, plan_duration_days in rows
    ]


def _build_member_checkin_payment_status(db: Session, member_id: UUID, reference_datetime: datetime) -> dict[str, object]:
    assigned_classes = _list_member_billing_assignments(db, member_id)
    if not assigned_classes:
        return {
            "message": "Check-in refused: member has no classes linked.",
            "member_id": str(member_id),
            "classes": [],
            "summary": {
                "assigned_class_count": 0,
                "paid_class_count": 0,
                "expired_class_count": 0,
                "pending_class_count": 0,
                "total_assigned_amount": "0.00",
                "total_pending_amount": "0.00",
            },
        }

    latest_coverages_by_class_id: dict[int, tuple[PaymentClassCoverage, Payment]] = {}
    rows = db.execute(
        select(PaymentClassCoverage, Payment)
        .join(Payment, Payment.id == PaymentClassCoverage.payment_id)
        .where(
            Payment.member_id == member_id,
            Payment.status == PaymentStatus.SUCCESS,
            PaymentClassCoverage.class_id.in_([int(item["class_id"]) for item in assigned_classes]),
        )
        .order_by(
            PaymentClassCoverage.class_id.asc(),
            PaymentClassCoverage.covered_from.desc(),
            PaymentClassCoverage.id.desc(),
        )
    ).all()

    for coverage, payment in rows:
        latest_coverages_by_class_id.setdefault(coverage.class_id, (coverage, payment))

    class_statuses: list[dict[str, object]] = []
    paid_class_count = 0
    expired_class_count = 0
    pending_class_count = 0
    total_assigned_amount = Decimal("0.00")
    total_pending_amount = Decimal("0.00")

    for assigned_class in assigned_classes:
        class_price = assigned_class["plan_price"]
        if not isinstance(class_price, Decimal):
            class_price = Decimal(str(class_price))

        total_assigned_amount += class_price
        class_id = int(assigned_class["class_id"])
        latest_coverage_row = latest_coverages_by_class_id.get(class_id)

        coverage_status = "payment_required"
        last_payment_id: int | None = None
        last_payment_at: datetime | None = None
        paid_from: datetime | None = None
        paid_until: datetime | None = None

        if latest_coverage_row is not None:
            latest_coverage, latest_payment = latest_coverage_row
            last_payment_id = latest_payment.id
            last_payment_at = latest_payment.created_at
            paid_from = latest_coverage.covered_from
            paid_until = latest_coverage.covered_until
            coverage_status = "paid" if reference_datetime <= _resolve_reference_datetime(latest_coverage.covered_until) else "expired"

        if coverage_status == "paid":
            paid_class_count += 1
        elif coverage_status == "expired":
            expired_class_count += 1
            total_pending_amount += class_price
        else:
            pending_class_count += 1
            total_pending_amount += class_price

        class_statuses.append(
            {
                "class_id": class_id,
                "title": assigned_class["class_title"],
                "plan_id": int(assigned_class["plan_id"]),
                "plan_name": assigned_class["plan_name"],
                "plan_price": _format_decimal_amount(class_price),
                "plan_duration_days": int(assigned_class["plan_duration_days"]),
                "status": coverage_status,
                "last_payment_id": last_payment_id,
                "last_payment_at": last_payment_at,
                "paid_from": paid_from,
                "paid_until": paid_until,
            }
        )

    summary = {
        "assigned_class_count": len(assigned_classes),
        "paid_class_count": paid_class_count,
        "expired_class_count": expired_class_count,
        "pending_class_count": pending_class_count,
        "total_assigned_amount": _format_decimal_amount(total_assigned_amount),
        "total_pending_amount": _format_decimal_amount(total_pending_amount),
    }

    return {
        "message": (
            "Check-in authorized: all assigned classes are paid and within validity."
            if pending_class_count == 0 and expired_class_count == 0
            else "Check-in refused: member has assigned classes with pending or expired payment coverage."
        ),
        "member_id": str(member_id),
        "classes": class_statuses,
        "summary": summary,
    }


def get_member_checkin_payment_status(
    db: Session,
    member_id: UUID,
    *,
    reference_datetime: datetime | None = None,
) -> dict[str, object]:
    member = get_member_by_id(db, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    return _build_member_checkin_payment_status(db, member_id, _resolve_reference_datetime(reference_datetime))


def _select_assigned_classes_for_payment(
    assigned_classes: list[dict[str, object]],
    selected_class_ids: list[int],
) -> list[dict[str, object]]:
    assigned_classes_by_id = {
        int(assigned_class["class_id"]): assigned_class
        for assigned_class in assigned_classes
    }
    unique_class_ids = list(dict.fromkeys(selected_class_ids))
    invalid_class_ids = [class_id for class_id in unique_class_ids if class_id not in assigned_classes_by_id]
    if invalid_class_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot register payment: selected classes are not assigned to this member. "
                f"Invalid ids: {', '.join(str(class_id) for class_id in invalid_class_ids)}."
            ),
        )

    return [assigned_classes_by_id[class_id] for class_id in unique_class_ids]


def list_member_summaries(db: Session) -> list[dict[str, object]]:
    rows = db.execute(
        select(Member, User)
        .join(User, User.id == Member.user_id)
        .order_by(User.full_name.asc(), User.email.asc())
    ).all()
    assignment_map = _build_member_assignment_map(db, [member.id for member, _ in rows])
    return [
        {
            "id": member.id,
            "user_id": member.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "cpf": member.cpf,
            "phone": member.phone,
            "assigned_class_count": len(assignment_map.get(member.id, {}).get("class_titles", [])),
            "assigned_plan_names": assignment_map.get(member.id, {}).get("plan_names", []),
            "status": member.status,
        }
        for member, user in rows
    ]


def list_member_reports(db: Session) -> list[dict[str, object]]:
    rows = db.execute(
        select(Member, User)
        .join(User, User.id == Member.user_id)
        .order_by(User.full_name.asc(), User.email.asc())
    ).all()
    assignment_map = _build_member_assignment_map(db, [member.id for member, _ in rows])
    return [
        {
            "id": member.id,
            "user_id": member.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "is_active": user.is_active,
            "assigned_class_titles": assignment_map.get(member.id, {}).get("class_titles", []),
            "assigned_plan_names": assignment_map.get(member.id, {}).get("plan_names", []),
            "cpf": member.cpf,
            "birth_date": member.birth_date,
            "phone": member.phone,
            "gender": member.gender,
            "photo_url": member.photo_url,
            "street": member.street,
            "number": member.number,
            "city": member.city,
            "state": member.state,
            "country": member.country,
            "zip_code": member.zip_code,
            "status": member.status,
            "created_at": member.created_at,
            "updated_at": member.updated_at,
        }
        for member, user in rows
    ]


def get_member_by_id(db: Session, member_id) -> Member | None:
    return db.execute(select(Member).where(Member.id == member_id)).scalar_one_or_none()


def _validate_member_dependencies(db: Session, member_in: MemberCreate) -> None:
    existing_member = db.execute(select(Member).where(Member.cpf == member_in.cpf)).scalar_one_or_none()
    if existing_member is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A member with this CPF already exists.")


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


def create_class(db: Session, class_in: ClassCreate) -> AcademyClass:
    selected_plan = db.execute(select(Plan).where(Plan.id == class_in.plan_id)).scalar_one_or_none()
    if selected_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Selected plan not found.")

    schedules = [
        {
            "day": schedule.day,
            "start_time": schedule.start_time.strftime("%H:%M"),
            "end_time": schedule.end_time.strftime("%H:%M"),
        }
        for schedule in class_in.schedules
    ]
    academy_class = AcademyClass(
        title=class_in.title,
        description=class_in.description,
        frequency=class_in.frequency,
        plan_id=class_in.plan_id,
        days=list(dict.fromkeys(schedule["day"] for schedule in schedules)),
        schedules=schedules,
    )
    db.add(academy_class)
    db.commit()
    db.refresh(academy_class)
    return academy_class


def list_classes(db: Session) -> list[AcademyClass]:
    return db.execute(select(AcademyClass).order_by(AcademyClass.title.asc(), AcademyClass.id.asc())).scalars().all()


def get_member_class_assignments(db: Session, member_id: UUID) -> dict[str, object]:
    member = get_member_by_id(db, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    rows = db.execute(
        select(MemberClassAssignment, AcademyClass)
        .join(AcademyClass, AcademyClass.id == MemberClassAssignment.class_id)
        .where(MemberClassAssignment.member_id == member_id)
        .order_by(AcademyClass.title.asc(), MemberClassAssignment.id.asc())
    ).all()

    return {
        "member_id": member_id,
        "classes": [
            {
                "assignment_id": assignment.id,
                "class_id": academy_class.id,
                "title": academy_class.title,
                "description": academy_class.description,
                "frequency": academy_class.frequency,
                "plan_id": academy_class.plan_id,
                "days": academy_class.days,
                "schedules": academy_class.schedules,
                "assigned_by": assignment.assigned_by,
                "assigned_at": assignment.assigned_at,
            }
            for assignment, academy_class in rows
        ],
    }


def replace_member_class_assignments(
    db: Session,
    member_id: UUID,
    payload: MemberClassAssignmentWrite,
    *,
    assigned_by: int,
) -> dict[str, object]:
    member = get_member_by_id(db, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    class_ids = list(dict.fromkeys(payload.class_ids))
    if class_ids:
        existing_class_ids = set(
            db.execute(select(AcademyClass.id).where(AcademyClass.id.in_(class_ids))).scalars().all()
        )
        missing_class_ids = [class_id for class_id in class_ids if class_id not in existing_class_ids]
        if missing_class_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Classes not found: {', '.join(str(class_id) for class_id in missing_class_ids)}.",
            )

    db.execute(delete(MemberClassAssignment).where(MemberClassAssignment.member_id == member_id))

    for class_id in class_ids:
        db.add(MemberClassAssignment(member_id=member_id, class_id=class_id, assigned_by=assigned_by))

    db.commit()
    return get_member_class_assignments(db, member_id)


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
        "operator_id": payment.operator_id,
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


def create_payment(db: Session, payment_in: PaymentCreate, *, operator_id: int) -> dict[str, object]:
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

    assigned_classes = _list_member_billing_assignments(db, payment_in.member_id)
    if not assigned_classes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot register payment: member has no assigned classes.",
        )

    selected_classes = _select_assigned_classes_for_payment(assigned_classes, payment_in.class_ids)

    total_assigned_amount = sum(
        (
            assigned_class["plan_price"]
            if isinstance(assigned_class["plan_price"], Decimal)
            else Decimal(str(assigned_class["plan_price"]))
        )
        for assigned_class in selected_classes
    )
    if payment_in.amount < total_assigned_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Payment amount does not cover the selected classes. "
                f"Required total: {_format_decimal_amount(total_assigned_amount)}."
            ),
        )

    payment_created_at = datetime.now(timezone.utc)

    payment = Payment(
        member_id=payment_in.member_id,
        amount=payment_in.amount,
        method_id=payment_in.method_id,
        operator_id=operator_id,
        status=PaymentStatus.SUCCESS,
        idempotency_key=f"pay-{uuid4().hex}",
        created_at=payment_created_at,
    )

    user.is_active = True
    db.add(user)
    db.add(member)
    db.add(payment)
    db.flush()

    for assigned_class in selected_classes:
        plan_duration_days = int(assigned_class["plan_duration_days"])
        db.add(
            PaymentClassCoverage(
                payment_id=payment.id,
                class_id=int(assigned_class["class_id"]),
                class_title_snapshot=str(assigned_class["class_title"]),
                plan_id_snapshot=int(assigned_class["plan_id"]),
                plan_name_snapshot=str(assigned_class["plan_name"]),
                plan_price_snapshot=(
                    assigned_class["plan_price"]
                    if isinstance(assigned_class["plan_price"], Decimal)
                    else Decimal(str(assigned_class["plan_price"]))
                ),
                plan_duration_days_snapshot=plan_duration_days,
                covered_from=payment_created_at,
                covered_until=payment_created_at + timedelta(days=plan_duration_days),
            )
        )

    db.flush()
    current_payment_status = _build_member_checkin_payment_status(db, payment_in.member_id, payment_created_at)
    member.status = (
        MemberStatus.ACTIVE
        if int(current_payment_status["summary"]["pending_class_count"]) == 0 and int(current_payment_status["summary"]["expired_class_count"]) == 0
        else MemberStatus.BLOCKED
    )
    db.add(member)

    db.commit()
    db.refresh(payment)
    return _build_payment_read(payment, payment_method)


def _resolve_reference_datetime(value: datetime | None) -> datetime:
    reference_datetime = value or datetime.now(timezone.utc)
    if reference_datetime.tzinfo is None:
        return reference_datetime.replace(tzinfo=timezone.utc)

    return reference_datetime.astimezone(timezone.utc)


def _block_member_for_payment_refusal(
    db: Session,
    member: Member,
    detail: str | dict[str, object],
    *,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> None:
    member.status = MemberStatus.BLOCKED
    db.add(member)
    db.commit()
    raise HTTPException(status_code=status_code, detail=detail)


def list_checkins(db: Session) -> list[Checkin]:
    return db.execute(select(Checkin).order_by(Checkin.checkin_datetime.desc())).scalars().all()


def create_checkin(db: Session, checkin_in: CheckinCreate) -> Checkin:
    member = get_member_by_id(db, checkin_in.member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    user = db.execute(select(User).where(User.id == member.user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for the selected member.")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in refused: linked user is inactive.",
        )

    if member.status == MemberStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Check-in refused: member status is '{member.status.value}'.",
        )

    reference_datetime = _resolve_reference_datetime(checkin_in.checkin_datetime)
    payment_status = _build_member_checkin_payment_status(db, member.id, reference_datetime)

    if int(payment_status["summary"]["assigned_class_count"]) == 0:
        _block_member_for_payment_refusal(
            db,
            member,
            payment_status,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if int(payment_status["summary"]["expired_class_count"]) > 0 or int(payment_status["summary"]["pending_class_count"]) > 0:
        _block_member_for_payment_refusal(
            db,
            member,
            payment_status,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
        )

    payload = checkin_in.model_dump(exclude_none=True)
    payload.setdefault("checkin_datetime", reference_datetime)
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