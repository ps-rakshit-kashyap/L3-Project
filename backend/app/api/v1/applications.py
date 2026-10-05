import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_authenticated_user, verify_candidate_ownership
from app.db.session import get_db
from app.models.application import Application
from app.models.user import User, UserRole
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.services.application_service import application_service
from app.services.candidate_service import candidate_service

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    application_in: ApplicationCreate,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    """Create a new job application (Candidates apply for self; Admins/Recruiters can apply for any)."""
    # Enforce candidate ownership if applicant is a candidate
    verify_candidate_ownership(application_in.candidate_id, current_user, db)

    try:
        application = application_service.create(db, application_in)
        return ApplicationResponse.model_validate(application)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    job_id: uuid.UUID | None = Query(default=None, description="Filter by job ID"),
    candidate_id: uuid.UUID | None = Query(default=None, description="Filter by candidate ID"),
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> list[ApplicationResponse]:
    """List applications with optional filters (Candidates restricted to own applications)."""
    user_role = (current_user.role or "").upper()

    if user_role == UserRole.CANDIDATE.value:
        own_candidate = candidate_service.get_by_user_or_email(
            db, user_id=current_user.id, email=current_user.email
        )
        if not own_candidate:
            return []

        # If a candidate_id was passed, it must match candidate's own ID
        if candidate_id and candidate_id != own_candidate.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot query applications of another candidate",
            )
        candidate_id = own_candidate.id

    applications = application_service.get_all(db, job_id=job_id, candidate_id=candidate_id)
    return [ApplicationResponse.model_validate(a) for a in applications]


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: uuid.UUID,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    """Get application by UUID (Admin/Recruiter or owner Candidate)."""
    application = application_service.get_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found",
        )

    # Verify ownership
    user_role = (current_user.role or "").upper()
    if user_role == UserRole.CANDIDATE.value:
        cand = application.candidate
        is_owner = (cand.user_id == current_user.id) or (
            cand.email.lower() == current_user.email.lower()
        )
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot view another candidate's application",
            )

    return ApplicationResponse.model_validate(application)

