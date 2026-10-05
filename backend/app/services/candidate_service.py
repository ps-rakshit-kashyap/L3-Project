import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.candidate import Candidate
from app.models.resume import Resume
from app.schemas.candidate import CandidateCreate


class CandidateService:
    @staticmethod
    def get_all(db: Session) -> Sequence[Candidate]:
        statement = (
            select(Candidate)
            .options(selectinload(Candidate.resumes))
            .order_by(Candidate.created_at.desc())
        )
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, candidate_id: uuid.UUID) -> Candidate | None:
        statement = (
            select(Candidate)
            .options(selectinload(Candidate.resumes))
            .where(Candidate.id == candidate_id)
        )
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_by_user_or_email(db: Session, user_id: uuid.UUID | None, email: str | None) -> Candidate | None:
        statement = select(Candidate).options(selectinload(Candidate.resumes))
        if user_id and email:
            statement = statement.where((Candidate.user_id == user_id) | (Candidate.email == email))
        elif user_id:
            statement = statement.where(Candidate.user_id == user_id)
        elif email:
            statement = statement.where(Candidate.email == email)
        else:
            return None
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def create(db: Session, candidate_in: CandidateCreate, user_id: uuid.UUID | None = None) -> Candidate:
        # Check email uniqueness
        existing = db.execute(
            select(Candidate).where(Candidate.email == candidate_in.email)
        ).scalar_one_or_none()
        if existing:
            raise ValueError(f"Candidate with email '{candidate_in.email}' already exists.")

        candidate = Candidate(
            user_id=user_id,
            name=candidate_in.name,
            email=candidate_in.email,
            phone=candidate_in.phone,
            location=candidate_in.location,
            profile_summary=candidate_in.profile_summary,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return candidate

    @staticmethod
    def attach_resume(
        db: Session,
        candidate_id: uuid.UUID,
        file_name: str,
        file_path: str,
        file_type: str,
    ) -> Resume:
        resume = Resume(
            candidate_id=candidate_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume


candidate_service = CandidateService()
