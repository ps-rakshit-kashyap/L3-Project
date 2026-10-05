from fastapi import APIRouter, status

from app.core.config import settings
from app.db import session as db_session
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    description="Verifies API availability and PostgreSQL database connectivity.",
)
def get_health() -> HealthResponse:
    db_connected, db_error = db_session.check_db_connection()

    overall_status = "healthy" if db_connected else "degraded"
    db_status = "connected" if db_connected else "disconnected"

    return HealthResponse(
        status=overall_status,
        api="available",
        database=db_status,
        environment=settings.APP_ENV,
        version=settings.VERSION,
        database_error=db_error if not db_connected else None,
    )
