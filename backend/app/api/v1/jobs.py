import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_authenticated_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.RECRUITER])),
    db: Session = Depends(get_db),
) -> JobResponse:
    """Create a new job posting (Admin and Recruiter only)."""
    try:
        job = job_service.create(db, job_in)
        return JobResponse.model_validate(job)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.get("", response_model=list[JobResponse])
def list_jobs(
    company_id: uuid.UUID | None = Query(default=None, description="Filter jobs by company"),
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> list[JobResponse]:
    """List all jobs (Authenticated users)."""
    jobs = job_service.get_all(db, company_id=company_id)
    return [JobResponse.model_validate(j) for j in jobs]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> JobResponse:
    """Get job by UUID (Authenticated users)."""
    job = job_service.get_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
    return JobResponse.model_validate(job)

