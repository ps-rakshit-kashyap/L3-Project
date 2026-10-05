from datetime import UTC, datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall service status ('healthy' or 'degraded')")
    api: str = Field(..., description="API availability status ('available')")
    database: str = Field(
        ..., description="Database connectivity status ('connected' or 'disconnected')"
    )
    environment: str = Field(
        ..., description="Application environment (development, staging, production)"
    )
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="UTC timestamp of the check"
    )
    database_error: str | None = Field(
        default=None, description="Error message if database connection failed"
    )
