import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate


class CompanyService:
    @staticmethod
    def get_all(db: Session) -> Sequence[Company]:
        statement = select(Company).order_by(Company.created_at.desc())
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, company_id: uuid.UUID) -> Company | None:
        statement = select(Company).where(Company.id == company_id)
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def create(db: Session, company_in: CompanyCreate) -> Company:
        company = Company(
            name=company_in.name,
            description=company_in.description,
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        return company


company_service = CompanyService()
