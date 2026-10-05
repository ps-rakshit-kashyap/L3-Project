import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApplicationBase(BaseModel):
    job_id: uuid.UUID = Field(..., description="Target job UUID")
    candidate_id: uuid.UUID = Field(..., description="Applying candidate UUID")
    status: str = Field(
        default="applied",
        max_length=50,
        description="Application status (applied, screening, interviewed, offered, rejected)",
    )


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationResponse(ApplicationBase):
    id: uuid.UUID
    applied_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
