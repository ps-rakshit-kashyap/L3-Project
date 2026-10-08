import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import require_role
from app.models.user import User, UserRole
from app.schemas.evaluation import EvaluationRunResponse, EvaluationResultResponse, EvaluationRunCreate
from app.models.evaluation_framework import EvaluationRun, EvaluationResultLog
from app.evaluation.engine import evaluation_engine

router = APIRouter(prefix="/evaluations", tags=["Evaluation"])

@router.post("/runs", response_model=EvaluationRunResponse)
def execute_evaluation_run(
    req: EvaluationRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.RECRUITER]))
):
    """Execute a new evaluation run against a dataset."""
    try:
        run = evaluation_engine.run_evaluation(db, req.dataset_name, req.agent_name, req.model_name)
        return run
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/runs/{id}", response_model=EvaluationRunResponse)
def get_evaluation_run(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.RECRUITER]))
):
    run = db.query(EvaluationRun).filter(EvaluationRun.id == id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.get("/runs/{id}/results", response_model=List[EvaluationResultResponse])
def get_evaluation_results(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.RECRUITER]))
):
    results = db.query(EvaluationResultLog).filter(EvaluationResultLog.run_id == id).all()
    return results
