import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.job import Job
from app.schemas.job import JobCreate


class JobService:
    @staticmethod
    def get_all(db: Session, company_id: uuid.UUID | None = None) -> Sequence[Job]:
        statement = select(Job).order_by(Job.created_at.desc())
        if company_id:
            statement = statement.where(Job.company_id == company_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, job_id: uuid.UUID) -> Job | None:
        statement = select(Job).where(Job.id == job_id)
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def create(db: Session, job_in: JobCreate) -> Job:
        # Verify company exists
        company = db.execute(
            select(Company).where(Company.id == job_in.company_id)
        ).scalar_one_or_none()
        if not company:
            raise ValueError(f"Company with ID {job_in.company_id} does not exist.")

        job = Job(
            company_id=job_in.company_id,
            title=job_in.title,
            description=job_in.description,
            requirements=job_in.requirements,
            location=job_in.location,
            employment_type=job_in.employment_type,
            status=job_in.status,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job


job_service = JobService()
