import io
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


def test_public_health_endpoint_no_token(unauthenticated_client: TestClient) -> None:
    """Verifies that the health endpoint remains public and accessible without authentication."""
    res = unauthenticated_client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_missing_token_returns_401(unauthenticated_client: TestClient) -> None:
    """Verifies that accessing protected endpoints without an Authorization header returns 401."""
    res = unauthenticated_client.get("/api/v1/auth/me")
    assert res.status_code == 401
    assert "Missing Bearer access token" in res.json()["detail"]


def test_invalid_token_returns_401(unauthenticated_client: TestClient) -> None:
    """Verifies that invalid or malformed tokens return 401."""
    res = unauthenticated_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.malformed.jwt.token"},
    )
    assert res.status_code == 401


def test_auth_me_returns_profile_and_role(
    admin_client: TestClient, recruiter_client: TestClient, candidate_client: TestClient
) -> None:
    """Verifies that /auth/me returns the correct user profile and role."""
    res_admin = admin_client.get("/api/v1/auth/me")
    assert res_admin.status_code == 200
    assert res_admin.json()["role"] == UserRole.ADMIN.value

    res_rec = recruiter_client.get("/api/v1/auth/me")
    assert res_rec.status_code == 200
    assert res_rec.json()["role"] == UserRole.RECRUITER.value

    res_cand = candidate_client.get("/api/v1/auth/me")
    assert res_cand.status_code == 200
    assert res_cand.json()["role"] == UserRole.CANDIDATE.value


def test_candidate_cannot_create_company_or_job(candidate_client: TestClient) -> None:
    """Verifies that Candidates receive 403 Forbidden when attempting to create companies or jobs."""
    # Attempt company creation
    res_co = candidate_client.post(
        "/api/v1/companies",
        json={"name": "Hacker Corp", "description": "Unauthorized"},
    )
    assert res_co.status_code == 403
    assert "Access denied" in res_co.json()["detail"]

    # Attempt job creation
    res_job = candidate_client.post(
        "/api/v1/jobs",
        json={
            "company_id": str(uuid.uuid4()),
            "title": "Unauthorized Job",
            "description": "Fail",
        },
    )
    assert res_job.status_code == 403
    assert "Access denied" in res_job.json()["detail"]


def test_candidate_cannot_list_all_candidates(candidate_client: TestClient) -> None:
    """Verifies that Candidates receive 403 Forbidden when trying to list all candidates."""
    res = candidate_client.get("/api/v1/candidates")
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]


def test_candidate_ownership_and_profile_access(
    candidate_client: TestClient, admin_client: TestClient
) -> None:
    """
    Verifies that Candidates can create and access their own profile,
    but receive 403 when attempting to access or create profiles for others.
    """
    # 1. Candidate creates own profile (email must match user email)
    cand_payload = {
        "name": "Candidate User",
        "email": "candidate@talentforge.ai",
        "profile_summary": "Passionate developer",
    }
    res_create = candidate_client.post("/api/v1/candidates", json=cand_payload)
    assert res_create.status_code == 201
    my_candidate_id = res_create.json()["id"]

    # 2. Candidate retrieves own profile via /candidates/me
    res_me = candidate_client.get("/api/v1/candidates/me")
    assert res_me.status_code == 200
    assert res_me.json()["id"] == my_candidate_id

    # 3. Candidate retrieves own profile via /candidates/{id}
    res_own = candidate_client.get(f"/api/v1/candidates/{my_candidate_id}")
    assert res_own.status_code == 200
    assert res_own.json()["name"] == "Candidate User"

    # 4. Admin creates another candidate
    other_payload = {
        "name": "Other Candidate",
        "email": "other_candidate@example.com",
        "profile_summary": "Another dev",
    }
    res_other = admin_client.post("/api/v1/candidates", json=other_payload)
    assert res_other.status_code == 201
    other_candidate_id = res_other.json()["id"]

    # 5. Candidate attempts to access other candidate's profile -> 403
    res_forbidden = candidate_client.get(f"/api/v1/candidates/{other_candidate_id}")
    assert res_forbidden.status_code == 403
    assert "cannot view or modify another candidate" in res_forbidden.json()["detail"]

    # 6. Candidate attempts to register profile with different email -> 403
    imposter_payload = {
        "name": "Imposter",
        "email": "victim@example.com",
    }
    res_imposter = candidate_client.post("/api/v1/candidates", json=imposter_payload)
    assert res_imposter.status_code == 403
    assert "different email address" in res_imposter.json()["detail"]


def test_candidate_resume_ownership(
    unauthenticated_client: TestClient, admin_client: TestClient
) -> None:
    """Verifies that candidates can only upload resumes to their own profile."""
    unique_cand_email = f"resume_cand_{uuid.uuid4().hex[:6]}@talentforge.ai"
    candidate_client = TestClient(
        unauthenticated_client.app,
        headers={"Authorization": f"Bearer test-token-{unique_cand_email}"},
    )

    # Create candidate profiles
    cand_res = candidate_client.post(
        "/api/v1/candidates",
        json={"name": "Owner", "email": unique_cand_email},
    )
    assert cand_res.status_code == 201
    my_candidate_id = cand_res.json()["id"]

    other_email = f"other_{uuid.uuid4().hex[:6]}@talentforge.ai"
    other_res = admin_client.post(
        "/api/v1/candidates",
        json={"name": "Other", "email": other_email},
    )
    assert other_res.status_code == 201
    other_candidate_id = other_res.json()["id"]

    # 1. Candidate uploads to own profile -> 201
    pdf_content = io.BytesIO(b"%PDF-1.4 Candidate resume")
    res_own_upload = candidate_client.post(
        f"/api/v1/candidates/{my_candidate_id}/resume",
        files={"file": ("my_resume.pdf", pdf_content, "application/pdf")},
    )
    assert res_own_upload.status_code == 201
    assert res_own_upload.json()["candidate_id"] == my_candidate_id

    # 2. Candidate attempts upload to other candidate's profile -> 403
    pdf_content_bad = io.BytesIO(b"%PDF-1.4 Malicious upload")
    res_bad_upload = candidate_client.post(
        f"/api/v1/candidates/{other_candidate_id}/resume",
        files={"file": ("hacked.pdf", pdf_content_bad, "application/pdf")},
    )
    assert res_bad_upload.status_code == 403
    assert "cannot view or modify another candidate" in res_bad_upload.json()["detail"]


def test_candidate_application_ownership(
    unauthenticated_client: TestClient, admin_client: TestClient
) -> None:
    """Verifies candidate application scoping and cross-candidate application prevention."""
    unique_app_cand_email = f"app_cand_{uuid.uuid4().hex[:6]}@talentforge.ai"
    candidate_client = TestClient(
        unauthenticated_client.app,
        headers={"Authorization": f"Bearer test-token-{unique_app_cand_email}"},
    )

    # Admin creates company and job
    co_res = admin_client.post("/api/v1/companies", json={"name": f"AuthCorp_{uuid.uuid4().hex[:4]}"})
    assert co_res.status_code == 201
    job_res = admin_client.post(
        "/api/v1/jobs",
        json={
            "company_id": co_res.json()["id"],
            "title": "Security Analyst",
            "description": "Analyze platform security and RBAC policies",
        },
    )
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # Candidate profile
    cand_res = candidate_client.post(
        "/api/v1/candidates",
        json={"name": "Applicant", "email": unique_app_cand_email},
    )
    assert cand_res.status_code == 201
    my_candidate_id = cand_res.json()["id"]

    # Other candidate
    other_email = f"stranger_{uuid.uuid4().hex[:6]}@talentforge.ai"
    other_res = admin_client.post(
        "/api/v1/candidates",
        json={"name": "Stranger", "email": other_email},
    )
    assert other_res.status_code == 201
    other_candidate_id = other_res.json()["id"]

    # 1. Candidate applies for self -> 201
    app_res = candidate_client.post(
        "/api/v1/applications",
        json={"job_id": job_id, "candidate_id": my_candidate_id},
    )
    assert app_res.status_code == 201
    my_app_id = app_res.json()["id"]

    # 2. Candidate attempts to apply on behalf of other candidate -> 403
    bad_app_res = candidate_client.post(
        "/api/v1/applications",
        json={"job_id": job_id, "candidate_id": other_candidate_id},
    )
    assert bad_app_res.status_code == 403

    # 3. Candidate lists applications -> only sees own application
    list_res = candidate_client.get("/api/v1/applications")
    assert list_res.status_code == 200
    apps = list_res.json()
    assert len(apps) == 1
    assert apps[0]["id"] == my_app_id

    # 4. Other application created by admin for stranger
    admin_app_res = admin_client.post(
        "/api/v1/applications",
        json={"job_id": job_id, "candidate_id": other_candidate_id},
    )
    assert admin_app_res.status_code == 201
    other_app_id = admin_app_res.json()["id"]

    # 5. Candidate attempts to get stranger's application -> 403
    get_forbidden = candidate_client.get(f"/api/v1/applications/{other_app_id}")
    assert get_forbidden.status_code == 403
    assert "Cannot view another candidate" in get_forbidden.json()["detail"]


def test_user_onboarding_and_role_promotion(
    admin_client: TestClient, recruiter_client: TestClient, candidate_client: TestClient
) -> None:
    """Verifies that new users default to CANDIDATE and only ADMIN can promote roles."""
    # 1. New user registers / syncs -> defaults to CANDIDATE
    res_sync = candidate_client.post("/api/v1/auth/sync", json={"name": "New Candidate"})
    assert res_sync.status_code == 200
    user_data = res_sync.json()
    assert user_data["role"] == UserRole.CANDIDATE.value
    user_id = user_data["id"]

    # 2. Recruiter attempts to promote user -> 403 Forbidden
    res_rec_promote = recruiter_client.patch(
        f"/api/v1/auth/users/{user_id}/role",
        json={"role": UserRole.RECRUITER.value},
    )
    assert res_rec_promote.status_code == 403

    # 3. Candidate attempts to promote own role -> 403 Forbidden
    res_cand_promote = candidate_client.patch(
        f"/api/v1/auth/users/{user_id}/role",
        json={"role": UserRole.ADMIN.value},
    )
    assert res_cand_promote.status_code == 403

    # 4. Admin promotes user to RECRUITER -> 200 OK
    res_admin_promote = admin_client.patch(
        f"/api/v1/auth/users/{user_id}/role",
        json={"role": UserRole.RECRUITER.value},
    )
    assert res_admin_promote.status_code == 200
    assert res_admin_promote.json()["role"] == UserRole.RECRUITER.value

    # 5. Admin lists users -> 200 OK
    res_users = admin_client.get("/api/v1/auth/users")
    assert res_users.status_code == 200
    assert any(u["id"] == user_id for u in res_users.json())
