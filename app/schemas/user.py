from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.user import UserRole, UserSector


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = UserRole.CLIENT
    sector: UserSector | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserProfileUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, max_length=255)
    sector: UserSector | None = None
    current_password: str | None = Field(default=None, min_length=8, max_length=128)
    new_password: str | None = Field(default=None, min_length=8, max_length=128)

    @model_validator(mode="after")
    def validate_password_change(self) -> "UserProfileUpdate":
        has_current_password = self.current_password is not None
        has_new_password = self.new_password is not None

        if has_current_password != has_new_password:
            raise ValueError("To change the password, provide both the current password and the new password.")

        return self


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)