import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.services.application_service import application_service

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    application_in: ApplicationCreate, db: Session = Depends(get_db)
) -> ApplicationResponse:
    """Create a new job application."""
    try:
        application = application_service.create(db, application_in)
        return ApplicationResponse.model_validate(application)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    job_id: uuid.UUID | None = Query(default=None, description="Filter by job ID"),
    candidate_id: uuid.UUID | None = Query(default=None, description="Filter by candidate ID"),
    db: Session = Depends(get_db),
) -> list[ApplicationResponse]:
    """List applications with optional filters."""
    applications = application_service.get_all(db, job_id=job_id, candidate_id=candidate_id)
    return [ApplicationResponse.model_validate(a) for a in applications]


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: uuid.UUID, db: Session = Depends(get_db)
) -> ApplicationResponse:
    """Get application by UUID."""
    application = application_service.get_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found",
        )
    return ApplicationResponse.model_validate(application)
