import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.company import Company
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User, UserRole

@pytest.fixture
def setup_interview_data(db_session: Session):
    company = Company(id=uuid.uuid4(), name="Tech Corp")
    db_session.add(company)
    job = Job(id=uuid.uuid4(), company_id=company.id, title="Engineer", description="Desc", status="open")
    db_session.add(job)
    cand = Candidate(id=uuid.uuid4(), name="Jane", email="jane@ex.com")
    db_session.add(cand)
    db_session.commit()
    
    resume = Resume(id=uuid.uuid4(), candidate_id=cand.id, file_name="res.pdf", file_path="res.pdf", file_type="pdf", extracted_text="Jane's resume with Python.")
    db_session.add(resume)
    app = Application(id=uuid.uuid4(), job_id=job.id, candidate_id=cand.id, status="applied")
    db_session.add(app)
    db_session.commit()
    return {"app": app, "cand": cand}

def test_interview_lifecycle(recruiter_client: TestClient, db_session: Session, setup_interview_data: dict, monkeypatch):
    app_id = setup_interview_data["app"].id
    
    # Create Interview
    res = recruiter_client.post(f"/api/v1/interviews?application_id={app_id}")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "CREATED"
    interview_id = data["id"]
    
    # Start
    res = recruiter_client.post(f"/api/v1/interviews/{interview_id}/start")
    assert res.status_code == 200
    assert res.json()["status"] == "IN_PROGRESS"
    
    # Get questions
    res = recruiter_client.get(f"/api/v1/interviews/{interview_id}/questions")
    assert res.status_code == 200
    questions = res.json()
    assert len(questions) == 4
    
    # Submit answer
    q_id = questions[0]["id"]
    res = recruiter_client.post(f"/api/v1/interviews/{interview_id}/answers?question_id={q_id}", json={"answer_text": "My answer"})
    assert res.status_code == 200
    
    # Complete
    res = recruiter_client.post(f"/api/v1/interviews/{interview_id}/complete")
    assert res.status_code == 200
    assert res.json()["status"] == "COMPLETED"
    
    # Evaluation
    res = recruiter_client.get(f"/api/v1/interviews/{interview_id}/evaluation")
    assert res.status_code == 200
    evals = res.json()
    assert len(evals) > 0
