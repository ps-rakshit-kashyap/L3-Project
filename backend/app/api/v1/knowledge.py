import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any

from app.core.auth import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.rag import KnowledgeDocument
from app.services.rag_service import rag_service

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

class KnowledgeIngestRequest(BaseModel):
    title: str
    text: str
    source_type: str = "generic"

class KnowledgeDocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    source_type: str
    
    model_config = {"from_attributes": True}

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    source_type: str | None = None

class SearchResponse(BaseModel):
    content: str
    document_id: uuid.UUID

@router.post("", response_model=KnowledgeDocumentResponse)
def ingest_knowledge(
    payload: KnowledgeIngestRequest,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.RECRUITER])),
    db: Session = Depends(get_db)
):
    """Ingest new knowledge document into RAG"""
    doc = rag_service.ingest_document(db, title=payload.title, source_type=payload.source_type, text=payload.text)
    return doc

@router.get("", response_model=list[KnowledgeDocumentResponse])
def list_knowledge(
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.RECRUITER])),
    db: Session = Depends(get_db)
):
    docs = db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()
    return docs

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge(
    document_id: uuid.UUID,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.RECRUITER])),
    db: Session = Depends(get_db)
):
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()

@router.post("/search", response_model=list[SearchResponse])
def search_knowledge(
    payload: SearchRequest,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.RECRUITER])),
    db: Session = Depends(get_db)
):
    chunks = rag_service.search(db, query=payload.query, top_k=payload.top_k, source_type=payload.source_type)
    return [{"content": c.content, "document_id": c.document_id} for c in chunks]
