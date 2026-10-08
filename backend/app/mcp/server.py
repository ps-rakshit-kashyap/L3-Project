import uuid
from mcp.server.mcpserver import MCPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.application import Application
from app.models.evaluation import ScreeningResult
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.services.rag_service import rag_service

mcp = MCPServer("TalentForge MCP Server")

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@mcp.tool()
def get_candidate(candidate_id: str) -> dict:
    with SessionLocal() as db:
        c = db.query(Candidate).filter(Candidate.id == uuid.UUID(candidate_id)).first()
        if not c:
            return {"error": "Candidate not found"}
        return {"id": str(c.id), "name": c.name, "email": c.email}

@mcp.tool()
def get_candidate_resume(candidate_id: str) -> list[dict]:
    with SessionLocal() as db:
        resumes = db.query(Resume).filter(Resume.candidate_id == uuid.UUID(candidate_id)).all()
        return [{"id": str(r.id), "file_name": r.file_name} for r in resumes]

@mcp.tool()
def get_resume_text(candidate_id: str) -> str:
    with SessionLocal() as db:
        resume = db.query(Resume).filter(Resume.candidate_id == uuid.UUID(candidate_id)).order_by(Resume.uploaded_at.desc()).first()
        if not resume:
            return "No resume found"
        return resume.extracted_text or "No text extracted"

@mcp.tool()
def get_job(job_id: str) -> dict:
    with SessionLocal() as db:
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        if not job:
            return {"error": "Job not found"}
        return {"title": job.title, "description": job.description}

@mcp.tool()
def get_job_requirements(job_id: str) -> dict:
    with SessionLocal() as db:
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        if not job:
            return {"error": "Job not found"}
        return {"requirements": job.requirements, "required_skills": job.required_skills, "preferred_skills": job.preferred_skills}

@mcp.tool()
def get_job_description(job_id: str) -> str:
    with SessionLocal() as db:
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        return job.description if job else "Job not found"

@mcp.tool()
def get_screening_result(application_id: str) -> dict:
    with SessionLocal() as db:
        res = db.query(ScreeningResult).filter(ScreeningResult.application_id == uuid.UUID(application_id)).first()
        if not res:
            return {"error": "Not found"}
        return {"score": res.score, "recommendation": res.recommendation, "summary": res.summary}

@mcp.tool()
def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    with SessionLocal() as db:
        chunks = rag_service.search(db, query=query, top_k=top_k)
        return [{"content": c.content, "source": c.document.title} for c in chunks]

if __name__ == "__main__":
    mcp.run()
