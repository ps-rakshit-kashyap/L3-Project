import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.user import User, UserRole
from app.services.orchestration_service import orchestration_service
from app.schemas.orchestration import OrchestrationRunResponse, OrchestrationEvaluateRequest
from app.models.orchestration import OrchestrationRun
from app.models.interview import InterviewSession
from fastapi import HTTPException

def check_interview_access(db: Session, interview_id: uuid.UUID, current_user: User):
    if current_user.role in [UserRole.ADMIN, UserRole.RECRUITER]:
        return
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session or (session.application.candidate.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")

router = APIRouter(prefix="/orchestration", tags=["Orchestration"])

@router.post("/interviews/{id}/generate", response_model=OrchestrationRunResponse)
def generate_interview(id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_interview_access(db, id, current_user)
    return orchestration_service.generate_questions_workflow(db, id)

@router.post("/interviews/{id}/evaluate", response_model=OrchestrationRunResponse)
def evaluate_interview(id: uuid.UUID, req: OrchestrationEvaluateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_interview_access(db, id, current_user)
    return orchestration_service.evaluate_answer_workflow(db, id, req.question_id, req.answer_text)

@router.post("/interviews/{id}/complete", response_model=OrchestrationRunResponse)
def complete_interview(id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_interview_access(db, id, current_user)
    return orchestration_service.complete_interview_workflow(db, id)

@router.get("/interviews/{id}/status", response_model=List[OrchestrationRunResponse])
def get_orchestration_status(id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_interview_access(db, id, current_user)
    runs = db.query(OrchestrationRun).filter(OrchestrationRun.interview_session_id == id).order_by(OrchestrationRun.started_at.desc()).all()
    return runs

@router.get("/interviews/{id}/trace", response_model=List[OrchestrationRunResponse])
def get_orchestration_trace(id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_interview_access(db, id, current_user)
    runs = db.query(OrchestrationRun).filter(OrchestrationRun.interview_session_id == id).order_by(OrchestrationRun.started_at.desc()).all()
    return runs
