from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.services.interview.question_generator import generate_questions
from app.services.interview.evaluators import evaluate_technical, evaluate_problem_solving, evaluate_communication, evaluate_role_fit
from app.services.interview.final_evaluator import evaluate_final
from app.schemas.interview import InterviewQuestionCreate, EvaluatorResult, FinalEvaluationResult

router = APIRouter(prefix="/agents", tags=["agents - development"])

from app.schemas.screening import ScreeningEvaluation
from app.services.screening_service import screening_agent
from app.models.job import Job

class QuestionGeneratorRequest(BaseModel):
    candidate_context: str
    job_context: str
    rubric_context: str

class ScreeningAgentRequest(BaseModel):
    job_title: str
    job_description: str
    job_requirements: str
    resume_text: str
    candidate_name: str | None = None
    custom_notes: str | None = None
    rag_context: str | None = None

@router.post("/screening/evaluate", summary="[DEV] Test Screening Agent", response_model=ScreeningEvaluation)
def test_evaluate_screening(req: ScreeningAgentRequest, current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.RECRUITER]))):
    """Directly invokes the Screening Agent."""
    mock_job = Job(title=req.job_title, description=req.job_description, requirements=req.job_requirements)
    return screening_agent.evaluate(
        job=mock_job,
        resume_text=req.resume_text,
        candidate_name=req.candidate_name,
        custom_notes=req.custom_notes,
        rag_context=req.rag_context,
    )

class AnswerEvaluatorRequest(BaseModel):
    question: str
    answer: str
    candidate_context: str
    job_context: str
    rubric_context: str

class FinalEvaluatorRequest(BaseModel):
    evaluations: List[Dict[str, Any]]

@router.post("/interview/generate-questions", summary="[DEV] Test Question Generator Agent", response_model=List[InterviewQuestionCreate])
def test_generate_questions(req: QuestionGeneratorRequest, current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.RECRUITER]))):
    """Directly invokes the Question Generator Agent without requiring a database InterviewSession."""
    return generate_questions(req.candidate_context, req.job_context, req.rubric_context)

@router.post("/interview/evaluate-technical", summary="[DEV] Test Technical Evaluator Agent", response_model=EvaluatorResult)
def test_evaluate_technical(req: AnswerEvaluatorRequest, current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.RECRUITER]))):
    """Directly invokes the Technical Answer Evaluator Agent."""
    return evaluate_technical(req.question, req.answer, req.candidate_context, req.job_context, req.rubric_context)

@router.post("/interview/evaluate-problem-solving", summary="[DEV] Test Problem Solving Evaluator Agent", response_model=EvaluatorResult)
def test_evaluate_problem_solving(req: AnswerEvaluatorRequest, current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.RECRUITER]))):
    """Directly invokes the Problem Solving Answer Evaluator Agent."""
    return evaluate_problem_solving(req.question, req.answer, req.candidate_context, req.job_context, req.rubric_context)

@router.post("/interview/evaluate-communication", summary="[DEV] Test Communication Evaluator Agent", response_model=EvaluatorResult)
def test_evaluate_communication(req: AnswerEvaluatorRequest, current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.RECRUITER]))):
    """Directly invokes the Communication Answer Evaluator Agent."""
    return evaluate_communication(req.question, req.answer, req.candidate_context, req.job_context, req.rubric_context)

@router.post("/interview/evaluate-role-fit", summary="[DEV] Test Role Fit Evaluator Agent", response_model=EvaluatorResult)
def test_evaluate_role_fit(req: AnswerEvaluatorRequest, current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.RECRUITER]))):
    """Directly invokes the Role Fit Answer Evaluator Agent."""
    return evaluate_role_fit(req.question, req.answer, req.candidate_context, req.job_context, req.rubric_context)

@router.post("/interview/evaluate-final", summary="[DEV] Test Final Evaluator Agent", response_model=FinalEvaluationResult)
def test_evaluate_final(req: FinalEvaluatorRequest, current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.RECRUITER]))):
    """Directly invokes the Final Evaluator Agent providing an aggregated summary from previous evaluations."""
    return evaluate_final(req.evaluations)
