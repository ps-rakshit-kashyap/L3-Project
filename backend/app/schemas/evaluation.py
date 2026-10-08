from typing import Any, List, Dict
from datetime import datetime
import uuid
from pydantic import BaseModel, Field

class EvaluationCase(BaseModel):
    case_id: str
    task_type: str
    input_context: Dict[str, Any]
    expected_output: Dict[str, Any]
    rubric: str | None = None
    metadata: Dict[str, Any] = {}

class MetricResult(BaseModel):
    metric_name: str
    score: float
    passed: bool
    details: str | None = None

class EvaluationResultCreate(BaseModel):
    case_id: str
    passed: bool
    metrics: Dict[str, Any]
    actual_output: Dict[str, Any]
    error_message: str | None = None
    latency_ms: int = 0

class EvaluationResultResponse(EvaluationResultCreate):
    id: uuid.UUID
    run_id: uuid.UUID
    class Config:
        from_attributes = True

class EvaluationRunCreate(BaseModel):
    agent_name: str
    dataset_name: str
    model_name: str = "mock"

class EvaluationRunResponse(BaseModel):
    id: uuid.UUID
    agent_name: str
    dataset_name: str
    model_name: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    total_cases: int
    passed_cases: int
    failed_cases: int
    accuracy: float
    results: List[EvaluationResultResponse] = []
    
    class Config:
        from_attributes = True

class EvaluationSummary(BaseModel):
    run_id: uuid.UUID
    agent_name: str
    cases: int
    passed: int
    failed: int
    accuracy: float
