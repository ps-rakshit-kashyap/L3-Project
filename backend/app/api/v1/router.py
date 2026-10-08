from fastapi import APIRouter

from app.api.v1.applications import router as applications_router
from app.api.v1.auth import router as auth_router
from app.api.v1.candidates import router as candidates_router
from app.api.v1.companies import router as companies_router
from app.api.v1.health import router as health_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.screenings import router as screenings_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.interviews import router as interviews_router
from app.api.v1.agents import router as agents_router
from app.api.v1.orchestration import router as orchestration_router
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.observability import router as observability_router

api_router = APIRouter()

# Include version 1 endpoints
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router)
api_router.include_router(companies_router)
api_router.include_router(jobs_router)
api_router.include_router(candidates_router)
api_router.include_router(applications_router)
api_router.include_router(screenings_router)
api_router.include_router(knowledge_router)
api_router.include_router(interviews_router)
api_router.include_router(agents_router)
api_router.include_router(orchestration_router)
api_router.include_router(evaluation_router)
api_router.include_router(observability_router)
