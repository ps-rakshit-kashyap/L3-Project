import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.company import CompanyCreate, CompanyResponse
from app.services.company_service import company_service

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(company_in: CompanyCreate, db: Session = Depends(get_db)) -> CompanyResponse:
    """Create a new company."""
    company = company_service.create(db, company_in)
    return CompanyResponse.model_validate(company)


@router.get("", response_model=list[CompanyResponse])
def list_companies(db: Session = Depends(get_db)) -> list[CompanyResponse]:
    """List all companies."""
    companies = company_service.get_all(db)
    return [CompanyResponse.model_validate(c) for c in companies]


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: uuid.UUID, db: Session = Depends(get_db)) -> CompanyResponse:
    """Get company by UUID."""
    company = company_service.get_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found",
        )
    return CompanyResponse.model_validate(company)
