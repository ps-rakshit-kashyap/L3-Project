import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.db.session import get_db, SessionLocal
from app.models.evaluation_framework import EvaluationRun
from app.schemas.evaluation import EvaluationCase

@pytest.fixture
def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer admin_token"}

def test_evaluation_cli_and_engine(override_get_db, auth_headers):
    # Test dataset loading and engine directly through a mocked evaluator call
    with patch("app.evaluation.engine.evaluate_technical") as mock_generate:
        mock_res = MagicMock()
        mock_res.score = 8.5
        mock_res.strengths = ["Strong"]
        mock_res.weaknesses = ["None"]
        mock_res.evidence = ["Evidence"]
        mock_res.rationale = "Good"
        mock_res.evaluator_type = "TECHNICAL"
        mock_res.model_dump.return_value = {
            "score": 8.5,
            "strengths": ["Strong"],
            "weaknesses": ["None"],
            "evidence": ["Evidence"],
            "rationale": "Good",
            "evaluator_type": "TECHNICAL"
        }
        mock_generate.return_value = mock_res
        
        # Write dummy dataset
        import json
        dataset = [
            {
                "case_id": "test-tech-1",
                "task_type": "technical_eval",
                "input_context": {
                    "question": "Q?",
                    "answer": "A!",
                    "resume_text": "Resume",
                    "job_context": "Job",
                    "rubric": "Rubric"
                },
                "expected_output": {
                    "score_min": 8.0,
                    "score_max": 9.0
                }
            }
        ]
        with open("data/eval_dataset.json", "w") as f:
            json.dump(dataset, f)
            
        client = TestClient(app)
        # We need an admin user in the DB to use the token
        # Mock auth for the API
        with patch("app.api.v1.evaluation.require_role") as mock_req_role:
            from app.models.user import User, UserRole
            mock_user = User(id="00000000-0000-0000-0000-000000000000", email="admin@test.com", role=UserRole.ADMIN)
            
            # Since Depends(require_role) is used, we can override the dependency on the app
            def override_require_role():
                return mock_user
            
            # Instead of complex auth overrides, let's just test the evaluation engine directly
            from app.evaluation.engine import evaluation_engine
            db = override_get_db
            run = evaluation_engine.run_evaluation(db, "data/eval_dataset.json", "technical_eval")
            
            assert run.total_cases == 1
            assert run.passed_cases == 1
            assert run.accuracy == 100.0
            assert run.status == "COMPLETED"

def test_evaluation_api_rbac():
    client = TestClient(app)
    # Without auth token, it should be 401
    res = client.post("/api/v1/evaluations/runs", json={
        "agent_name": "technical_eval",
        "dataset_name": "data/eval_dataset.json"
    })
    assert res.status_code == 401
