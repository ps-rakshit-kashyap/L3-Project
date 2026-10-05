from fastapi import APIRouter

from app.api.v1.applications import router as applications_router
from app.api.v1.candidates import router as candidates_router
from app.api.v1.companies import router as companies_router
from app.api.v1.health import router as health_router
from app.api.v1.jobs import router as jobs_router

api_router = APIRouter()

# Include version 1 endpoints
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(companies_router)
api_router.include_router(jobs_router)
api_router.include_router(candidates_router)
api_router.include_router(applications_router)
