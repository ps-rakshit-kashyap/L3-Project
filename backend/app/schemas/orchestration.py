from typing import Any, List
from datetime import datetime
import uuid
from pydantic import BaseModel

class AgentExecutionResponse(BaseModel):
    id: uuid.UUID
    agent_name: str
    task: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    error_message: str | None

class OrchestrationRunResponse(BaseModel):
    id: uuid.UUID
    interview_session_id: uuid.UUID
    status: str
    workflow_type: str
    started_at: datetime
    completed_at: datetime | None
    error_message: str | None
    executions: List[AgentExecutionResponse] = []

    class Config:
        from_attributes = True

class OrchestrationGenerateRequest(BaseModel):
    pass

class OrchestrationEvaluateRequest(BaseModel):
    question_id: uuid.UUID
    answer_text: str

class OrchestrationCompleteRequest(BaseModel):
    pass
