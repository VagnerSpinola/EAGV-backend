from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.deps import CurrentAdmin, CurrentUser, DbSession
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserProfileUpdate, UserRead
from app.services.auth import (
    authenticate_user,
    create_user,
    get_user_by_id,
    issue_access_token,
    issue_password_reset_token,
    reset_user_password,
    update_user_image,
    update_current_user,
)
from app.services.user_images import upload_user_image


router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: DbSession) -> UserRead:
    user = create_user(db, user_in=user_in)
    return UserRead.model_validate(user)


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_by_admin(user_in: UserCreate, _: CurrentAdmin, db: DbSession) -> UserRead:
    user = create_user(db, user_in=user_in)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: DbSession) -> TokenResponse:
    user = authenticate_user(db, email=credentials.email, password=credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = issue_access_token(user.email)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: DbSession) -> ForgotPasswordResponse:
    reset_token = issue_password_reset_token(db, email=payload.email)
    return ForgotPasswordResponse(
        message="If the account exists, password recovery instructions have been generated.",
        reset_token=reset_token,
    )


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: DbSession) -> dict[str, str]:
    reset_user_password(db, token=payload.token, new_password=payload.new_password)
    return {"message": "Password updated successfully."}


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=TokenResponse)
def update_me(payload: UserProfileUpdate, current_user: CurrentUser, db: DbSession) -> TokenResponse:
    user = update_current_user(db, user=current_user, user_in=payload)
    access_token = issue_access_token(user.email)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/me/image", response_model=TokenResponse)
def upload_me_image(current_user: CurrentUser, db: DbSession, file: UploadFile = File(...)) -> TokenResponse:
    image_url = upload_user_image(file=file, user_id=current_user.id)
    user = update_user_image(db, user=current_user, image_url=image_url)
    access_token = issue_access_token(user.email)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/users/{user_id}/image", response_model=UserRead)
def upload_user_image_by_admin(user_id: int, _: CurrentAdmin, db: DbSession, file: UploadFile = File(...)) -> UserRead:
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    image_url = upload_user_image(file=file, user_id=user_id)
    updated_user = update_user_image(db, user=user, image_url=image_url)
    return UserRead.model_validate(updated_user)