import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.interview import InterviewSession
from app.schemas.interview import InterviewSessionSchema, InterviewQuestionSchema, InterviewAnswerCreate, InterviewAnswerSchema, InterviewEvaluationSchema
from app.services.interview_service import interview_service

router = APIRouter(prefix="/interviews", tags=["interviews"])

def verify_access(db: Session, current_user: User, interview: InterviewSession):
    if current_user.role == UserRole.CANDIDATE:
        if interview.candidate.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this interview")

@router.post("", response_model=InterviewSessionSchema)
def create_interview(application_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.RECRUITER]:
        raise HTTPException(status_code=403, detail="Not authorized to create interviews")
    return interview_service.create_interview(db, application_id)

@router.get("/{interview_id}", response_model=InterviewSessionSchema)
def get_interview(interview_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    verify_access(db, current_user, session)
    return session

@router.post("/{interview_id}/start", response_model=InterviewSessionSchema)
def start_interview(interview_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    verify_access(db, current_user, session)
    return interview_service.start_interview(db, interview_id)

@router.get("/{interview_id}/questions", response_model=List[InterviewQuestionSchema])
def get_interview_questions(interview_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    verify_access(db, current_user, session)
    return session.questions

@router.post("/{interview_id}/answers", response_model=InterviewAnswerSchema)
def submit_answer(interview_id: uuid.UUID, question_id: uuid.UUID, answer: InterviewAnswerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    verify_access(db, current_user, session)
    if current_user.role == UserRole.CANDIDATE and session.status != "IN_PROGRESS":
        raise HTTPException(status_code=400, detail="Interview is not in progress")
    return interview_service.submit_answer(db, interview_id, question_id, answer.answer_text)

@router.post("/{interview_id}/complete", response_model=InterviewSessionSchema)
def complete_interview(interview_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    verify_access(db, current_user, session)
    return interview_service.complete_interview(db, interview_id)

@router.get("/{interview_id}/evaluation", response_model=List[InterviewEvaluationSchema])
def get_evaluation(interview_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    verify_access(db, current_user, session)
    if current_user.role == UserRole.CANDIDATE and session.status != "COMPLETED":
        raise HTTPException(status_code=403, detail="Evaluation not yet available")
    return session.evaluations
