from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/observability/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "langfuse_configured" in data

def test_config_endpoint():
    response = client.get("/api/v1/observability/config")
    assert response.status_code == 200
    data = response.json()
    assert "langfuse_base_url" in data
    assert "tracing_enabled" in data
