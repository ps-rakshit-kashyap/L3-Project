from fastapi.testclient import TestClient

from app.db import session as db_session


def test_root_endpoint(client: TestClient) -> None:
    """Verifies that the root endpoint returns 200 and basic API metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert data["docs_url"] == "/api/v1/docs"
    assert data["health_check"] == "/api/v1/health"


def test_health_endpoint_healthy(client: TestClient, monkeypatch) -> None:
    """Verifies that /api/v1/health returns HTTP 200 and healthy status when DB is connected."""
    monkeypatch.setattr(db_session, "check_db_connection", lambda: (True, None))

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["api"] == "available"
    assert data["database"] == "connected"
    assert data["database_error"] is None
    assert "timestamp" in data
    assert "version" in data


def test_health_endpoint_degraded_when_db_down(client: TestClient, monkeypatch) -> None:
    """Verifies that /api/v1/health reports degraded status when DB is disconnected."""
    error_msg = "could not connect to server: Connection refused"
    monkeypatch.setattr(db_session, "check_db_connection", lambda: (False, error_msg))

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["api"] == "available"
    assert data["database"] == "disconnected"
    assert data["database_error"] == error_msg


def test_check_db_connection_function() -> None:
    """Directly tests the check_db_connection utility return types."""
    is_connected, error = db_session.check_db_connection()
    assert isinstance(is_connected, bool)
    if not is_connected:
        assert error is not None
