import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    description: str = Field(..., min_length=1, description="Job description")
    requirements: str | None = Field(default=None, description="Job requirements or qualifications")
    required_skills: str | None = Field(default=None, description="Key required technical and domain skills")
    preferred_skills: str | None = Field(default=None, description="Nice-to-have or preferred skills")
    required_experience: str | None = Field(default=None, max_length=255, description="Years and depth of experience required")
    education_requirements: str | None = Field(default=None, max_length=255, description="Required education or degree level")
    location: str | None = Field(default="Remote", max_length=255, description="Location")
    employment_type: str = Field(
        default="Full-time",
        max_length=50,
        description="Employment type (Full-time, Contract, etc.)",
    )
    status: str = Field(
        default="open", max_length=50, description="Job status (open, closed, draft)"
    )


class JobCreate(JobBase):
    company_id: uuid.UUID = Field(..., description="ID of the hiring company")


class JobResponse(JobBase):
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
