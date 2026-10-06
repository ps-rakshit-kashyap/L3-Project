import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_roles
from app.db.session import get_db
from app.models.application import Application
from app.models.evaluation import ScreeningResult
from app.models.user import User, UserRole
from app.schemas.screening import ScreeningResultResponse, ScreeningTriggerRequest
from app.services.candidate_service import candidate_service
from app.services.resume_extractor import (
    CorruptResumeFileError,
    EmptyResumeContentError,
    UnsupportedResumeFormatError,
)
from app.services.screening_service import screening_agent

router = APIRouter(prefix="/screenings", tags=["Screenings"])


@router.post(
    "/applications/{application_id}",
    response_model=ScreeningResultResponse,
    status_code=status.HTTP_200_OK,
)
def screen_application(
    application_id: uuid.UUID,
    payload: ScreeningTriggerRequest | None = None,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.RECRUITER])),
    db: Session = Depends(get_db),
) -> ScreeningResultResponse:
    """
    Trigger the AI Screening Agent to evaluate a candidate's resume against the job description.
    Restricted to Admins and Recruiters.
    """
    force_rescreen = payload.force_rescreen if payload else False
    custom_notes = payload.custom_notes if payload else None

    try:
        result = screening_agent.screen_application(
            db=db,
            application_id=application_id,
            force_rescreen=force_rescreen,
            custom_notes=custom_notes,
        )
        return ScreeningResultResponse.model_validate(result)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except (UnsupportedResumeFormatError, EmptyResumeContentError, CorruptResumeFileError) as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Screening evaluation failed: {exc}",
        )


@router.get("/applications/{application_id}", response_model=ScreeningResultResponse)
def get_screening_for_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScreeningResultResponse:
    """
    Retrieve the screening result for a given application.
    Recruiters/Admins can view any result; candidates can view only their own.
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found",
        )

    # Candidate access restriction
    user_role = (current_user.role or "").upper()
    if user_role == UserRole.CANDIDATE.value:
        cand = application.candidate
        is_owner = (cand.user_id == current_user.id) or (
            cand.email.lower() == current_user.email.lower()
        )
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot view screening results of another candidate",
            )

    result = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.application_id == application_id)
        .first()
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No screening evaluation has been performed for this application yet.",
        )

    return ScreeningResultResponse.model_validate(result)


@router.get("/{screening_id}", response_model=ScreeningResultResponse)
def get_screening_by_id(
    screening_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScreeningResultResponse:
    """Retrieve a screening result by UUID."""
    result = db.query(ScreeningResult).filter(ScreeningResult.id == screening_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening result with ID {screening_id} not found",
        )

    # Candidate ownership verification
    user_role = (current_user.role or "").upper()
    if user_role == UserRole.CANDIDATE.value:
        cand = result.application.candidate
        is_owner = (cand.user_id == current_user.id) or (
            cand.email.lower() == current_user.email.lower()
        )
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot view another candidate's screening evaluation",
            )

    return ScreeningResultResponse.model_validate(result)


@router.get("", response_model=list[ScreeningResultResponse])
def list_screenings(
    job_id: uuid.UUID | None = Query(default=None, description="Filter by job ID"),
    passed: bool | None = Query(default=None, description="Filter by passed status"),
    recommendation: str | None = Query(default=None, description="Filter by recommendation"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ScreeningResultResponse]:
    """List screening results with optional filters."""
    user_role = (current_user.role or "").upper()

    query = db.query(ScreeningResult).join(Application, ScreeningResult.application_id == Application.id)

    if user_role == UserRole.CANDIDATE.value:
        own_candidate = candidate_service.get_by_user_or_email(
            db, user_id=current_user.id, email=current_user.email
        )
        if not own_candidate:
            return []
        query = query.filter(Application.candidate_id == own_candidate.id)

    if job_id:
        query = query.filter(Application.job_id == job_id)
    if passed is not None:
        query = query.filter(ScreeningResult.passed == passed)
    if recommendation:
        query = query.filter(ScreeningResult.recommendation == recommendation.upper())

    results = query.order_by(ScreeningResult.created_at.desc()).all()
    return [ScreeningResultResponse.model_validate(r) for r in results]
