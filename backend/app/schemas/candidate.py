import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.resume import ResumeResponse


class CandidateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Full name")
    email: EmailStr = Field(..., description="Unique email address")
    phone: str | None = Field(default=None, max_length=50, description="Contact phone number")
    location: str | None = Field(default=None, max_length=255, description="Current location")
    profile_summary: str | None = Field(default=None, description="Candidate summary or background")


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    resumes: list[ResumeResponse] = []

    model_config = ConfigDict(from_attributes=True)
