import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.candidate import Candidate
from app.models.job import Job
from app.schemas.application import ApplicationCreate


class ApplicationService:
    @staticmethod
    def get_all(
        db: Session,
        job_id: uuid.UUID | None = None,
        candidate_id: uuid.UUID | None = None,
    ) -> Sequence[Application]:
        statement = select(Application).order_by(Application.applied_at.desc())
        if job_id:
            statement = statement.where(Application.job_id == job_id)
        if candidate_id:
            statement = statement.where(Application.candidate_id == candidate_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, application_id: uuid.UUID) -> Application | None:
        statement = select(Application).where(Application.id == application_id)
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def create(db: Session, application_in: ApplicationCreate) -> Application:
        # Verify job and candidate exist
        job = db.execute(select(Job).where(Job.id == application_in.job_id)).scalar_one_or_none()
        if not job:
            raise ValueError(f"Job with ID {application_in.job_id} does not exist.")

        candidate = db.execute(
            select(Candidate).where(Candidate.id == application_in.candidate_id)
        ).scalar_one_or_none()
        if not candidate:
            raise ValueError(f"Candidate with ID {application_in.candidate_id} does not exist.")

        application = Application(
            job_id=application_in.job_id,
            candidate_id=application_in.candidate_id,
            status=application_in.status,
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        return application


application_service = ApplicationService()
