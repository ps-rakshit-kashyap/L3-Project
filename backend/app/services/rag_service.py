import re
import uuid
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.models.rag import KnowledgeDocument, DocumentChunk

class RAGService:
    """Minimal RAG service for document ingestion and retrieval."""

    def __init__(self):
        self.chunk_size = 1000

    def get_embedding(self, text: str) -> list[float]:
        """Calls OpenAI embedding API directly."""
        api_key = settings.EMBEDDING_API_KEY
        if not api_key:
            # Ponytail: mock if missing
            return [0.0] * 1536
            
        base_url = settings.EMBEDDING_BASE_URL.rstrip("/")
        endpoint = f"{base_url}/embeddings"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "input": text,
            "model": settings.EMBEDDING_MODEL,
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["embedding"]
        except Exception:
            # Fallback for testing/offline
            return [0.0] * 1536

    def chunk_text(self, text: str) -> list[str]:
        """Simple split by double newline, preserving some size constraints."""
        paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]
        chunks = []
        current_chunk = []
        current_length = 0
        
        for p in paragraphs:
            if current_length + len(p) > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [p]
                current_length = len(p)
            else:
                current_chunk.append(p)
                current_length += len(p)
                
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
            
        return chunks if chunks else [text]

    def ingest_document(self, db: Session, title: str, source_type: str, text: str) -> KnowledgeDocument:
        doc = KnowledgeDocument(title=title, source_type=source_type)
        db.add(doc)
        db.flush()
        
        chunks = self.chunk_text(text)
        for i, chunk_content in enumerate(chunks):
            embedding = self.get_embedding(chunk_content)
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=i,
                content=chunk_content,
                embedding=embedding
            )
            db.add(chunk)
            
        db.commit()
        db.refresh(doc)
        return doc

    def search(self, db: Session, query: str, top_k: int = 5, source_type: str | None = None) -> list[DocumentChunk]:
        query_embedding = self.get_embedding(query)
        
        stmt = select(DocumentChunk).join(KnowledgeDocument)
        if source_type:
            stmt = stmt.where(KnowledgeDocument.source_type == source_type)
            
        # pgvector L2 distance (or cosine distance with <=>)
        if db.bind.dialect.name == "postgresql":
            stmt = stmt.order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        
        stmt = stmt.limit(top_k)
        
        return list(db.scalars(stmt))

rag_service = RAGService()
