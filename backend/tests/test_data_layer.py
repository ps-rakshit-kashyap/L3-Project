import io
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.rag import DocumentChunk, KnowledgeDocument


def test_companies_crud(client: TestClient) -> None:
    # 1. Create company
    payload = {"name": "Acme Corp", "description": "AI-first robotics and hiring"}
    res = client.post("/api/v1/companies", json=payload)
    assert res.status_code == 201
    company = res.json()
    assert company["name"] == "Acme Corp"
    assert "id" in company
    company_id = company["id"]

    # 2. List companies
    res_list = client.get("/api/v1/companies")
    assert res_list.status_code == 200
    ids = [c["id"] for c in res_list.json()]
    assert company_id in ids

    # 3. Get single company
    res_get = client.get(f"/api/v1/companies/{company_id}")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Acme Corp"

    # 4. Missing company (404)
    missing_id = str(uuid.uuid4())
    res_missing = client.get(f"/api/v1/companies/{missing_id}")
    assert res_missing.status_code == 404


def test_jobs_crud_and_foreign_key(client: TestClient) -> None:
    # 1. Create company first
    res_co = client.post(
        "/api/v1/companies",
        json={"name": "TechFlow", "description": "Cloud infra"},
    )
    company_id = res_co.json()["id"]

    # 2. Create job with valid company_id
    job_payload = {
        "company_id": company_id,
        "title": "Staff Backend Engineer",
        "description": "Build high-throughput event processing pipelines",
        "requirements": "Python, FastAPI, PostgreSQL",
        "location": "Remote",
        "employment_type": "Full-time",
        "status": "open",
    }
    res_job = client.post("/api/v1/jobs", json=job_payload)
    assert res_job.status_code == 201
    job = res_job.json()
    assert job["title"] == "Staff Backend Engineer"
    job_id = job["id"]

    # 3. Get single job
    res_get = client.get(f"/api/v1/jobs/{job_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == job_id

    # 4. Foreign key constraint violation check (invalid company_id)
    invalid_job = {
        "company_id": str(uuid.uuid4()),
        "title": "Orphan Job",
        "description": "This should fail",
    }
    res_bad = client.post("/api/v1/jobs", json=invalid_job)
    assert res_bad.status_code == 404
    assert "does not exist" in res_bad.json()["detail"]


def test_candidates_crud_and_uniqueness(client: TestClient) -> None:
    unique_email = f"candidate_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "name": "Jane Doe",
        "email": unique_email,
        "phone": "+1-555-0199",
        "location": "San Francisco, CA",
        "profile_summary": "Principal Software Architect with 10 years experience",
    }
    # 1. Create candidate
    res = client.post("/api/v1/candidates", json=payload)
    assert res.status_code == 201
    candidate = res.json()
    assert candidate["email"] == unique_email
    candidate_id = candidate["id"]

    # 2. Duplicate email check (should return 400 Bad Request)
    res_dup = client.post("/api/v1/candidates", json=payload)
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["detail"]

    # 3. Get candidate
    res_get = client.get(f"/api/v1/candidates/{candidate_id}")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Jane Doe"


def test_applications_crud(client: TestClient) -> None:
    # Setup company, job, and candidate
    co_res = client.post("/api/v1/companies", json={"name": "DevShop"})
    job_res = client.post(
        "/api/v1/jobs",
        json={"company_id": co_res.json()["id"], "title": "Dev", "description": "Coding"},
    )
    cand_res = client.post(
        "/api/v1/candidates",
        json={"name": "Bob", "email": f"bob_{uuid.uuid4().hex[:6]}@example.com"},
    )

    # 1. Create application
    app_payload = {
        "job_id": job_res.json()["id"],
        "candidate_id": cand_res.json()["id"],
        "status": "applied",
    }
    res = client.post("/api/v1/applications", json=app_payload)
    assert res.status_code == 201
    app_id = res.json()["id"]

    # 2. Get application
    res_get = client.get(f"/api/v1/applications/{app_id}")
    assert res_get.status_code == 200
    assert res_get.json()["status"] == "applied"


def test_resume_upload_and_validation(client: TestClient) -> None:
    cand_res = client.post(
        "/api/v1/candidates",
        json={"name": "Alice", "email": f"alice_{uuid.uuid4().hex[:6]}@example.com"},
    )
    candidate_id = cand_res.json()["id"]

    # 1. Successful resume upload (.pdf)
    fake_pdf = io.BytesIO(b"%PDF-1.4 Mock resume content for testing purposes")
    files = {"file": ("alice_resume.pdf", fake_pdf, "application/pdf")}
    res_upload = client.post(f"/api/v1/candidates/{candidate_id}/resume", files=files)
    assert res_upload.status_code == 201
    resume_data = res_upload.json()
    assert resume_data["file_name"] == "alice_resume.pdf"
    assert resume_data["candidate_id"] == candidate_id
    assert "resumes/" in resume_data["file_path"]

    # 2. Candidate now has the resume attached
    res_cand = client.get(f"/api/v1/candidates/{candidate_id}")
    assert len(res_cand.json()["resumes"]) == 1

    # 3. Invalid extension upload (.exe)
    fake_exe = io.BytesIO(b"malicious payload")
    res_bad_ext = client.post(
        f"/api/v1/candidates/{candidate_id}/resume",
        files={"file": ("virus.exe", fake_exe, "application/octet-stream")},
    )
    assert res_bad_ext.status_code == 400
    assert "Unsupported file extension" in res_bad_ext.json()["detail"]

    # 4. Empty file upload
    empty_file = io.BytesIO(b"")
    res_empty = client.post(
        f"/api/v1/candidates/{candidate_id}/resume",
        files={"file": ("empty.pdf", empty_file, "application/pdf")},
    )
    assert res_empty.status_code == 400
    assert "empty" in res_empty.json()["detail"]

    # 5. Non-existent candidate
    missing_id = str(uuid.uuid4())
    valid_pdf = io.BytesIO(b"%PDF-1.4 Mock content")
    res_missing = client.post(
        f"/api/v1/candidates/{missing_id}/resume",
        files={"file": ("test.pdf", valid_pdf, "application/pdf")},
    )
    assert res_missing.status_code == 404


def test_pgvector_rag_foundation_model(db_session: Session) -> None:
    """Verifies that KnowledgeDocument and DocumentChunk with vector embedding can be stored."""
    doc = KnowledgeDocument(
        title="Engineering Evaluation Rubric",
        source_type="rubric",
        doc_metadata={"department": "Engineering"},
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    # 1536-dimensional mock embedding vector
    mock_vec = [0.01 * (i % 10) for i in range(1536)]
    chunk = DocumentChunk(
        document_id=doc.id,
        chunk_index=0,
        content="Candidate demonstrates deep proficiency in distributed systems design.",
        embedding=mock_vec,
        chunk_metadata={"section": "architecture"},
    )
    db_session.add(chunk)
    db_session.commit()
    db_session.refresh(chunk)

    assert chunk.document_id == doc.id
    assert chunk.content.startswith("Candidate demonstrates")
    assert chunk.embedding is not None
