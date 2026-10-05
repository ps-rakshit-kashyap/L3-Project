import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Provides a TestClient for FastAPI endpoints."""
    with TestClient(app) as test_client:
        yield test_client
