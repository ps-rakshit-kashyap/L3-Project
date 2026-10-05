from fastapi import APIRouter

from app.api.v1.health import router as health_router

api_router = APIRouter()

# Include version 1 endpoints
api_router.include_router(health_router, tags=["Health"])
