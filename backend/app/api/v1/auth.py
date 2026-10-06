import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserRoleUpdate, UserSignupRequest, UserSyncRequest
from app.services.storage import storage_service

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup_user(
    body: UserSignupRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Onboards a new candidate user using Supabase Auth Admin API and provisions profile in PostgreSQL.
    - Password is sent securely to Supabase Auth (never stored in PostgreSQL).
    - Email is auto-confirmed to avoid SMTP rate limits and MX validation errors on test/mock domains.
    - Assigned role is strictly CANDIDATE.
    """
    if len(body.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long",
        )

    clean_email = str(body.email).strip().lower()
    existing_user = db.query(User).filter(User.email == clean_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{clean_email}' already exists",
        )

    if not storage_service.client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable",
        )

    try:
        sb_res = storage_service.client.auth.admin.create_user({
            "email": clean_email,
            "password": body.password,
            "email_confirm": True,
            "user_metadata": {"name": body.name.strip()},
        })
        sb_user = sb_res.user
        if not sb_user or not sb_user.id:
            raise ValueError("No user returned from Supabase Auth admin API")
        auth_user_id = uuid.UUID(sb_user.id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {exc}",
        )

    new_user = User(
        id=uuid.uuid4(),
        auth_user_id=auth_user_id,
        name=body.name.strip(),
        email=clean_email,
        role=UserRole.CANDIDATE.value,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse.model_validate(new_user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Returns the authenticated user's profile and RBAC role."""
    return UserResponse.model_validate(current_user)


@router.post("/sync", response_model=UserResponse)
def sync_user(
    body: UserSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Syncs user information after Supabase signup/login.
    Default role remains CANDIDATE (users cannot self-promote to RECRUITER or ADMIN).
    """
    if body.name and body.name.strip():
        current_user.name = body.name.strip()
        db.commit()
        db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: uuid.UUID,
    role_in: UserRoleUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Admin-only endpoint: promote or update an application user's role.
    Only ADMIN can change user roles to RECRUITER, ADMIN, or CANDIDATE.
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    target_user.role = role_in.role.value
    db.commit()
    db.refresh(target_user)
    return UserResponse.model_validate(target_user)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    """Admin-only endpoint: list all application users."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserResponse.model_validate(u) for u in users]
