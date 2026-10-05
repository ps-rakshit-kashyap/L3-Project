import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    file_name: str
    file_path: str
    file_type: str
    uploaded_at: datetime
    file_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
