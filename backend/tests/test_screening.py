import io
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import docx
from pypdf import PdfWriter

from app.models.application import Application
from app.models.candidate import Candidate
from app.models.company import Company
from app.models.evaluation import ScreeningResult
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.screening import ScreeningRecommendation
from app.services.resume_extractor import (
    EmptyResumeContentError,
    UnsupportedResumeFormatError,
    resume_extractor,
)
from app.services.screening_service import screening_agent


def create_sample_docx_bytes() -> bytes:
    """Creates in-memory DOCX bytes for testing."""
    doc = docx.Document()
    doc.add_heading("Jane Candidate - Senior Python Engineer", 0)
    doc.add_paragraph("Summary: Experienced backend software engineer with 5+ years of experience.")
    doc.add_paragraph("Skills: Python, FastAPI, PostgreSQL, Docker, AWS, Git.")
    doc.add_paragraph("Experience: Senior Developer at TechCorp. Built scalable microservices using FastAPI and SQLAlchemy.")
    doc.add_paragraph("Education: Bachelor of Science in Computer Science, Tech University.")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def create_sample_pdf_bytes() -> bytes:
    """Creates valid in-memory PDF bytes with text annotations/metadata for testing."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=72, height=72)
    # Write metadata and a text comment
    writer.add_metadata({
        "/Title": "Resume of Jane Doe",
        "/Subject": "Experienced software engineer with 4 years Python and PostgreSQL.",
    })
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_txt_resume_extraction():
    """Verify clean text extraction from plain text bytes."""
    raw_txt = (
        "John Doe\n"
        "Software Engineer with 4 years of experience building Python and FastAPI applications.\n"
        "Education: B.S. in Computer Science."
    ).encode("utf-8")

    text = resume_extractor.extract_text_from_bytes(raw_txt, "resume.txt", "text/plain")
    assert "John Doe" in text
    assert "Python" in text
    assert "FastAPI" in text


def test_docx_resume_extraction():
    """Verify text extraction from DOCX file bytes."""
    docx_bytes = create_sample_docx_bytes()
    text = resume_extractor.extract_text_from_bytes(
        docx_bytes, "resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert "Senior Python Engineer" in text
    assert "FastAPI" in text
    assert "Docker" in text
    assert "Tech University" in text


def test_unsupported_and_empty_file_handling():
    """Verify error handling on unsupported or empty resume files."""
    # 0 bytes
    with pytest.raises(EmptyResumeContentError):
        resume_extractor.extract_text_from_bytes(b"", "empty.txt", "text/plain")

    # Unsupported format (.exe)
    with pytest.raises(UnsupportedResumeFormatError):
        resume_extractor.extract_text_from_bytes(b"A" * 100, "malware.exe", "application/octet-stream")

    # Too short (< 20 chars)
    with pytest.raises(EmptyResumeContentError):
        resume_extractor.extract_text_from_bytes(b"Hi there", "short.txt", "text/plain")


def test_screening_agent_heuristic_evaluation():
    """Verify that the screening agent accurately evaluates skills, experience, and score."""
    sample_job = Job(
        id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        title="Senior Python Backend Developer",
        description="Looking for an experienced engineer to build high-scale APIs with Python and FastAPI.",
        required_skills="Python, FastAPI, PostgreSQL, Docker",
        preferred_skills="AWS, Redis",
        required_experience="4+ years",
        education_requirements="Bachelor's in Computer Science",
        status="open",
    )

    resume_text = (
        "Jane Doe - Backend Developer\n"
        "Experience: 5+ years of software development experience.\n"
        "Extensive work with Python, FastAPI, PostgreSQL, and Docker in production.\n"
        "Education: Bachelor of Science in Computer Science."
    )

    result = screening_agent.evaluate(sample_job, resume_text, candidate_name="Jane Doe")

    assert result.overall_score >= 70.0
    assert result.recommendation == ScreeningRecommendation.ADVANCE
    assert result.passed is True
    assert len(result.skills_analysis) >= 4
    # Check that Python and FastAPI are marked as matched
    matched_skills = [s.skill.lower() for s in result.skills_analysis if s.matched]
    assert "python" in matched_skills
    assert "fastapi" in matched_skills
    assert len(result.strengths) > 0
    assert len(result.recommended_interview_questions) > 0


@pytest.fixture
def setup_application_with_resume(db_session: Session):
    """Sets up a complete company -> job -> candidate -> resume -> application hierarchy."""
    company = Company(id=uuid.uuid4(), name="Screening Tech Corp")
    db_session.add(company)

    job = Job(
        id=uuid.uuid4(),
        company_id=company.id,
        title="Full Stack Engineer",
        description="Seeking an engineer with Python, React, and TypeScript expertise.",
        required_skills="Python, React, TypeScript",
        preferred_skills="Docker",
        required_experience="3+ years",
        status="open",
    )
    db_session.add(job)

    uid = uuid.uuid4().hex[:8]
    candidate = Candidate(
        id=uuid.uuid4(),
        name=f"Candidate Jane {uid}",
        email=f"candidate.{uid}@example.com",
    )
    db_session.add(candidate)
    db_session.commit()

    # Pre-cache extracted text on Resume to avoid real network storage call in unit test
    resume = Resume(
        id=uuid.uuid4(),
        candidate_id=candidate.id,
        file_name="jane_resume.txt",
        file_path=f"resumes/{candidate.id}/jane_resume.txt",
        file_type="text/plain",
        extracted_text=(
            "Jane Candidate\n"
            "Full Stack Engineer with 4 years experience in Python, React, and TypeScript.\n"
            "Built responsive enterprise web applications.\n"
            "Education: B.S. in Computer Science."
        ),
    )
    db_session.add(resume)

    application = Application(
        id=uuid.uuid4(),
        job_id=job.id,
        candidate_id=candidate.id,
        status="applied",
    )
    db_session.add(application)
    db_session.commit()

    return {
        "company": company,
        "job": job,
        "candidate": candidate,
        "resume": resume,
        "application": application,
    }


def test_recruiter_can_trigger_screening(
    recruiter_client: TestClient,
    setup_application_with_resume: dict,
    db_session: Session,
):
    """Recruiters can trigger AI screening and retrieve structured evaluation."""
    app_id = setup_application_with_resume["application"].id

    res = recruiter_client.post(f"/api/v1/screenings/applications/{app_id}")
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["application_id"] == str(app_id)
    assert data["score"] is not None
    assert data["recommendation"] in ["ADVANCE", "HOLD", "REJECT"]
    assert "details" in data
    assert "skills_analysis" in data["details"]

    # Verify application status was updated to screened
    updated_app = db_session.query(Application).filter(Application.id == app_id).first()
    assert updated_app.status == "screened"


def test_candidate_forbidden_to_trigger_screening(
    unauthenticated_client: TestClient,
    setup_application_with_resume: dict,
):
    """Candidates are strictly forbidden from triggering screening evaluations."""
    cand_client = TestClient(
        unauthenticated_client.app,
        headers={"Authorization": "Bearer test-token-screening_forbidden_cand@talentforge.ai"},
    )
    app_id = setup_application_with_resume["application"].id
    res = cand_client.post(f"/api/v1/screenings/applications/{app_id}")
    assert res.status_code == 403


def test_candidate_can_view_own_screening_result(
    unauthenticated_client: TestClient,
    recruiter_client: TestClient,
    setup_application_with_resume: dict,
    db_session: Session,
):
    """Candidates can view their own screening results, but not other candidates'."""
    from app.models.user import User, UserRole

    app_id = setup_application_with_resume["application"].id

    # Recruiter triggers screening
    recruiter_client.post(f"/api/v1/screenings/applications/{app_id}")

    # Isolated candidate user
    email = "screening_cand_view@talentforge.ai"
    cand_client = TestClient(
        unauthenticated_client.app,
        headers={"Authorization": f"Bearer test-token-{email}"},
    )

    user = User(
        id=uuid.uuid4(),
        email=email,
        name="Candidate View",
        role=UserRole.CANDIDATE.value,
    )
    db_session.add(user)
    db_session.commit()

    cand = setup_application_with_resume["candidate"]
    cand.user_id = user.id
    db_session.add(cand)
    db_session.commit()

    # Candidate views own result
    res = cand_client.get(f"/api/v1/screenings/applications/{app_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["application_id"] == str(app_id)

    # If candidate is unlinked from this user, access is denied
    cand.user_id = uuid.uuid4()
    db_session.add(cand)
    db_session.commit()

    res_blocked = cand_client.get(f"/api/v1/screenings/applications/{app_id}")
    assert res_blocked.status_code == 403
