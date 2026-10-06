import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserResponse(BaseModel):
    id: uuid.UUID
    auth_user_id: uuid.UUID | None = None
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSyncRequest(BaseModel):
    name: str | None = None


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserSignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

