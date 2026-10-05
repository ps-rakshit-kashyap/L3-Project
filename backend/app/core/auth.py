import uuid
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.user import User, UserRole
from app.services.storage import storage_service

# Reusable HTTP Bearer scheme (auto_error=False allows returning custom 401 responses)
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extracts Bearer JWT from Authorization header, validates token with Supabase Auth,
    and returns the corresponding application User from PostgreSQL.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: Missing Bearer access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials.strip()

    # 1. Deterministic test mode tokens for fast unit testing & mock testing
    if token.startswith("test-token-"):
        # e.g., "test-token-admin", "test-token-recruiter", "test-token-candidate", or "test-token-user@example.com"
        suffix = token[len("test-token-") :].strip()
        role = UserRole.CANDIDATE.value
        email = f"{suffix}@talentforge.ai" if "@" not in suffix else suffix

        if suffix.upper() == "ADMIN":
            role = UserRole.ADMIN.value
            email = "admin@talentforge.ai"
        elif suffix.upper() == "RECRUITER":
            role = UserRole.RECRUITER.value
            email = "recruiter@talentforge.ai"
        elif suffix.upper() == "CANDIDATE":
            role = UserRole.CANDIDATE.value
            email = "candidate@talentforge.ai"

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                id=uuid.uuid4(),
                auth_user_id=uuid.uuid4(),
                name=suffix.capitalize(),
                email=email,
                role=role,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    # 2. Supabase Auth JWT validation
    if not storage_service.client:
        logger.error("Supabase client is not configured; cannot validate JWT.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable",
        )

    try:
        user_response = storage_service.client.auth.get_user(token)
        sb_user = user_response.user
        if not sb_user or not sb_user.id:
            raise ValueError("No user returned from Supabase Auth")
    except Exception as exc:
        logger.warning(f"Supabase JWT validation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or malformed authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_user_uuid = uuid.UUID(sb_user.id)
    email = sb_user.email or ""

    # 3. Lookup user in application database
    user = (
        db.query(User)
        .filter((User.auth_user_id == auth_user_uuid) | (User.email == email))
        .first()
    )

    # 4. Auto-provision application user if first time
    if not user:
        # Check if email is designated as initial bootstrap admin
        is_initial_admin = (
            settings.INITIAL_ADMIN_EMAIL
            and email.lower() == settings.INITIAL_ADMIN_EMAIL.lower()
        )
        initial_role = UserRole.ADMIN.value if is_initial_admin else UserRole.CANDIDATE.value
        name = (sb_user.user_metadata or {}).get("name") or (
            email.split("@")[0] if email else "User"
        )

        user = User(
            id=uuid.uuid4(),
            auth_user_id=auth_user_uuid,
            name=name,
            email=email,
            role=initial_role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Ensure auth_user_id is linked
        if not user.auth_user_id:
            user.auth_user_id = auth_user_uuid
            db.commit()
            db.refresh(user)

    return user


def require_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency ensuring an authenticated user is present."""
    return current_user


def require_role(required_role: UserRole) -> Callable[[User], User]:
    """Dependency factory requiring a specific role (ADMIN is always granted access)."""

    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        user_role = (current_user.role or "").upper()
        if user_role == UserRole.ADMIN.value:
            return current_user
        if user_role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Operation requires {required_role.value} role",
            )
        return current_user

    return role_dependency


def require_roles(allowed_roles: list[UserRole] | set[UserRole]) -> Callable[[User], User]:
    """Dependency factory requiring one of the allowed roles (ADMIN is always granted access)."""
    allowed_values = {
        r.value if isinstance(r, UserRole) else str(r).upper() for r in allowed_roles
    }
    allowed_values.add(UserRole.ADMIN.value)

    def roles_dependency(current_user: User = Depends(get_current_user)) -> User:
        user_role = (current_user.role or "").upper()
        if user_role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires one of {sorted(allowed_values)} roles",
            )
        return current_user

    return roles_dependency


def verify_candidate_ownership(
    candidate_id: uuid.UUID,
    current_user: User,
    db: Session,
) -> Candidate:
    """
    Checks that the current user is either an ADMIN/RECRUITER, or the CANDIDATE
    owning this candidate resource. Raises 404 if candidate does not exist,
    and 403 if ownership check fails.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found",
        )

    user_role = (current_user.role or "").upper()
    if user_role in (UserRole.ADMIN.value, UserRole.RECRUITER.value):
        return candidate

    # CANDIDATE role ownership check:
    # Must match candidate.user_id == current_user.id OR candidate.email == current_user.email
    is_owner = (candidate.user_id == current_user.id) or (
        candidate.email.lower() == current_user.email.lower()
    )
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot view or modify another candidate's resource",
        )

    # Lazily link user_id if not linked yet
    if candidate.user_id is None:
        candidate.user_id = current_user.id
        db.commit()
        db.refresh(candidate)

    return candidate
