from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError

from app.api.deps import CurrentAdmin, CurrentUser, DbSession
from app.schemas.academy import (
    BodyMeasurementCreate,
    BodyMeasurementRead,
    ClassCreate,
    MemberClassAssignmentsRead,
    MemberClassAssignmentWrite,
    ClassRead,
    CheckinCreate,
    CheckinPaymentStatusRead,
    CheckinRead,
    MemberCreate,
    MemberEnrollmentCreate,
    MemberRead,
    MemberReportRead,
    MemberSummaryRead,
    PaymentCreate,
    PaymentMethodCreate,
    PaymentMethodRead,
    PaymentRead,
    PlanCreate,
    PlanRead,
)
from app.services.academy import (
    create_body_measurement,
    create_class,
    create_checkin,
    create_member,
    create_member_enrollment,
    create_payment,
    create_payment_method,
    create_plan,
    get_member_checkin_payment_status,
    get_member_class_assignments,
    list_body_measurements,
    list_checkins,
    list_classes,
    list_member_payment_history,
    list_member_reports,
    list_member_summaries,
    list_payment_methods,
    list_payments,
    list_plans,
    replace_member_class_assignments,
)


router = APIRouter()


@router.get("/members", response_model=list[MemberSummaryRead])
def read_members(_: CurrentAdmin, db: DbSession) -> list[MemberSummaryRead]:
    return [MemberSummaryRead.model_validate(item) for item in list_member_summaries(db)]


@router.get("/members/report", response_model=list[MemberReportRead])
def read_member_reports(_: CurrentAdmin, db: DbSession) -> list[MemberReportRead]:
    return [MemberReportRead.model_validate(item) for item in list_member_reports(db)]


@router.post("/members", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member_record(payload: MemberCreate, _: CurrentAdmin, db: DbSession) -> MemberRead:
    return MemberRead.model_validate(create_member(db, payload))


@router.post("/members/with-image", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member_record_with_image(
    _: CurrentAdmin,
    db: DbSession,
    payload: str = Form(...),
    file: UploadFile = File(...),
) -> MemberRead:
    try:
        member_payload = MemberCreate.model_validate_json(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc

    return MemberRead.model_validate(create_member(db, member_payload, photo_file=file))


@router.post("/members/enrollment", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member_enrollment_record(
    current_admin: CurrentAdmin,
    db: DbSession,
    payload: str = Form(...),
    file: UploadFile | None = File(default=None),
) -> MemberRead:
    try:
        enrollment_payload = MemberEnrollmentCreate.model_validate_json(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc

    return MemberRead.model_validate(
        create_member_enrollment(
            db,
            enrollment_payload,
            created_by=current_admin.id,
            photo_file=file,
        )
    )


@router.get("/plans", response_model=list[PlanRead])
def read_plans(_: CurrentAdmin, db: DbSession) -> list[PlanRead]:
    return [PlanRead.model_validate(item) for item in list_plans(db)]


@router.post("/plans", response_model=PlanRead, status_code=status.HTTP_201_CREATED)
def create_plan_record(payload: PlanCreate, _: CurrentAdmin, db: DbSession) -> PlanRead:
    return PlanRead.model_validate(create_plan(db, payload))


@router.post("/classes", response_model=ClassRead, status_code=status.HTTP_201_CREATED)
def create_class_record(payload: ClassCreate, _: CurrentAdmin, db: DbSession) -> ClassRead:
    return ClassRead.model_validate(create_class(db, payload))


@router.get("/classes", response_model=list[ClassRead])
def read_classes(_: CurrentAdmin, db: DbSession) -> list[ClassRead]:
    return [ClassRead.model_validate(item) for item in list_classes(db)]


@router.get("/members/{member_id}/class-assignments", response_model=MemberClassAssignmentsRead)
def read_member_class_assignments(member_id: UUID, _: CurrentAdmin, db: DbSession) -> MemberClassAssignmentsRead:
    return MemberClassAssignmentsRead.model_validate(get_member_class_assignments(db, member_id))


@router.get("/members/{member_id}/checkin-payment-status", response_model=CheckinPaymentStatusRead)
def read_member_checkin_payment_status(
    member_id: UUID,
    _: CurrentAdmin,
    db: DbSession,
    reference_datetime: datetime | None = None,
) -> CheckinPaymentStatusRead:
    return CheckinPaymentStatusRead.model_validate(
        get_member_checkin_payment_status(db, member_id, reference_datetime=reference_datetime)
    )


@router.put("/members/{member_id}/class-assignments", response_model=MemberClassAssignmentsRead)
def replace_member_class_assignment_records(
    member_id: UUID,
    payload: MemberClassAssignmentWrite,
    current_user: CurrentUser,
    db: DbSession,
) -> MemberClassAssignmentsRead:
    return MemberClassAssignmentsRead.model_validate(
        replace_member_class_assignments(db, member_id, payload, assigned_by=current_user.id)
    )


@router.get("/payments", response_model=list[PaymentRead])
def read_payments(_: CurrentAdmin, db: DbSession) -> list[PaymentRead]:
    return [PaymentRead.model_validate(item) for item in list_payments(db)]


@router.get("/payments/members/{member_id}/history", response_model=list[PaymentRead])
def read_member_payment_history(member_id: UUID, _: CurrentAdmin, db: DbSession) -> list[PaymentRead]:
    return [PaymentRead.model_validate(item) for item in list_member_payment_history(db, member_id)]


@router.post("/payments", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment_record(payload: PaymentCreate, current_user: CurrentUser, db: DbSession) -> PaymentRead:
    return PaymentRead.model_validate(create_payment(db, payload, operator_id=current_user.id))


@router.get("/payment-methods", response_model=list[PaymentMethodRead])
def read_payment_methods(_: CurrentAdmin, db: DbSession) -> list[PaymentMethodRead]:
    return [PaymentMethodRead.model_validate(item) for item in list_payment_methods(db)]


@router.post("/payment-methods", response_model=PaymentMethodRead, status_code=status.HTTP_201_CREATED)
def create_payment_method_record(payload: PaymentMethodCreate, _: CurrentAdmin, db: DbSession) -> PaymentMethodRead:
    return PaymentMethodRead.model_validate(create_payment_method(db, payload))


@router.get("/checkins", response_model=list[CheckinRead])
def read_checkins(_: CurrentAdmin, db: DbSession) -> list[CheckinRead]:
    return [CheckinRead.model_validate(item) for item in list_checkins(db)]


@router.post("/checkins", response_model=CheckinRead, status_code=status.HTTP_201_CREATED)
def create_checkin_record(payload: CheckinCreate, _: CurrentAdmin, db: DbSession) -> CheckinRead:
    return CheckinRead.model_validate(create_checkin(db, payload))


@router.get("/body-measurements", response_model=list[BodyMeasurementRead])
def read_body_measurements(_: CurrentAdmin, db: DbSession) -> list[BodyMeasurementRead]:
    return [BodyMeasurementRead.model_validate(item) for item in list_body_measurements(db)]


@router.post("/body-measurements", response_model=BodyMeasurementRead, status_code=status.HTTP_201_CREATED)
def create_body_measurement_record(
    payload: BodyMeasurementCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> BodyMeasurementRead:
    return BodyMeasurementRead.model_validate(
        create_body_measurement(db, payload, created_by=current_user.id)
    )