import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class InterviewQuestionBase(BaseModel):
    question: str
    category: str
    difficulty: str
    competency: str
    evaluation_criteria: List[str]
    order_index: int

class InterviewQuestionCreate(InterviewQuestionBase):
    pass

class InterviewQuestionSchema(InterviewQuestionBase):
    id: uuid.UUID
    interview_session_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InterviewAnswerBase(BaseModel):
    answer_text: str

class InterviewAnswerCreate(InterviewAnswerBase):
    pass

class InterviewAnswerSchema(InterviewAnswerBase):
    id: uuid.UUID
    interview_question_id: uuid.UUID
    interview_session_id: uuid.UUID
    submitted_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InterviewEvaluationSchema(BaseModel):
    id: uuid.UUID
    interview_session_id: uuid.UUID
    question_id: Optional[uuid.UUID]
    evaluator_type: str
    score: Optional[float]
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    evidence: Optional[str]
    rationale: Optional[str]
    structured_result: Optional[Dict[str, Any]]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InterviewSessionSchema(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    status: str
    current_question_index: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    questions: Optional[List[InterviewQuestionSchema]] = None
    evaluations: Optional[List[InterviewEvaluationSchema]] = None
    model_config = ConfigDict(from_attributes=True)

class EvaluatorResult(BaseModel):
    score: float
    strengths: List[str]
    weaknesses: List[str]
    evidence: str
    rationale: str

class FinalEvaluationResult(BaseModel):
    technical_score: float
    problem_solving_score: float
    communication_score: float
    role_fit_score: float
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    evidence: str
    summary: str
    recommendation: str
