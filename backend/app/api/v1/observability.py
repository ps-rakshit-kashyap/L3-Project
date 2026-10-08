from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/observability", tags=["Observability"])

@router.get("/health")
def get_health():
    """Check observability configuration health."""
    has_keys = bool(settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY)
    return {
        "status": "ok" if has_keys else "degraded",
        "langfuse_configured": has_keys
    }

@router.get("/config")
def get_config():
    """Return non-sensitive observability configuration."""
    return {
        "langfuse_base_url": settings.LANGFUSE_BASE_URL,
        "tracing_enabled": bool(settings.LANGFUSE_PUBLIC_KEY)
    }
