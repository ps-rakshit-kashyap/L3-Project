import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth import (
    get_current_user,
    require_authenticated_user,
    require_roles,
    verify_candidate_ownership,
)
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.candidate import CandidateCreate, CandidateResponse
from app.schemas.resume import ResumeResponse
from app.services.candidate_service import candidate_service
from app.services.storage import storage_service

router = APIRouter(prefix="/candidates", tags=["Candidates"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_FILE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(
    candidate_in: CandidateCreate,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> CandidateResponse:
    """Create a new candidate profile (Candidates create own profile; Admins/Recruiters can create any)."""
    user_role = (current_user.role or "").upper()
    link_user_id = None

    if user_role == UserRole.CANDIDATE.value:
        # Candidate can only create a profile with their own email
        if candidate_in.email.lower() != current_user.email.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Candidates cannot register profiles under a different email address",
            )
        link_user_id = current_user.id
    elif user_role in (UserRole.ADMIN.value, UserRole.RECRUITER.value):
        # Admin or Recruiter can optionally link or leave unlinked
        link_user_id = None

    try:
        candidate = candidate_service.create(db, candidate_in, user_id=link_user_id)
        return CandidateResponse.model_validate(candidate)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("/me", response_model=CandidateResponse)
def get_my_candidate_profile(
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> CandidateResponse:
    """Get the current authenticated user's own candidate profile."""
    candidate = candidate_service.get_by_user_or_email(
        db, user_id=current_user.id, email=current_user.email
    )
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found for the current user",
        )
    return CandidateResponse.model_validate(candidate)


@router.get("", response_model=list[CandidateResponse])
def list_candidates(
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.RECRUITER])),
    db: Session = Depends(get_db),
) -> list[CandidateResponse]:
    """List all candidates (Admin and Recruiter only)."""
    candidates = candidate_service.get_all(db)
    return [CandidateResponse.model_validate(c) for c in candidates]


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: uuid.UUID,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> CandidateResponse:
    """Get candidate by UUID (Admin/Recruiter or owner Candidate)."""
    candidate = verify_candidate_ownership(candidate_id, current_user, db)
    return CandidateResponse.model_validate(candidate)


@router.post(
    "/{candidate_id}/resume",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_candidate_resume(
    candidate_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> ResumeResponse:
    """
    Upload a resume file for a candidate to Supabase Storage and register in database.
    Owner candidate or Admin/Recruiter only.
    """
    # Verify resource ownership
    candidate = verify_candidate_ownership(candidate_id, current_user, db)

    # Validate file extension
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{suffix}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Read and validate file content
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )

    # Upload to storage
    content_type = file.content_type or "application/octet-stream"
    upload_res = storage_service.upload_file(
        file_bytes=content,
        original_name=file.filename or "resume.pdf",
        content_type=content_type,
        candidate_id=candidate.id,
    )

    # Persist resume record in database
    resume = candidate_service.attach_resume(
        db=db,
        candidate_id=candidate.id,
        file_name=upload_res["file_name"],
        file_path=upload_res["file_path"],
        file_type=upload_res["file_type"],
    )

    response = ResumeResponse.model_validate(resume)
    response.file_url = upload_res.get("file_url")
    return response

