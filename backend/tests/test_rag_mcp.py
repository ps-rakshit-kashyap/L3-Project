import pytest
from sqlalchemy.orm import Session
from app.services.rag_service import rag_service
from app.models.rag import KnowledgeDocument, DocumentChunk

def test_chunking():
    # Force small chunk size to test splitting
    rag_service.chunk_size = 15
    text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
    chunks = rag_service.chunk_text(text)
    rag_service.chunk_size = 1000 # restore
    assert len(chunks) == 3
    assert chunks[0] == "Paragraph 1"

def test_ingestion_and_search(db_session: Session, monkeypatch):
    # Mock embeddings to avoid real API calls during test
    def mock_get_embedding(text):
        return [0.1] * 1536
    
    monkeypatch.setattr(rag_service, "get_embedding", mock_get_embedding)
    
    doc = rag_service.ingest_document(db_session, title="Test Doc", source_type="policy", text="This is a test policy document.\n\nIt has rules.")
    assert doc.id is not None
    assert doc.title == "Test Doc"
    
    # Check chunks in DB
    chunks = db_session.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
    assert len(chunks) == 1
    
    # Test Search
    results = rag_service.search(db_session, query="rules", top_k=5)
    assert len(results) > 0
    assert doc.id in [r.document_id for r in results]

def test_empty_retrieval(db_session: Session, monkeypatch):
    def mock_get_embedding(text):
        return [0.1] * 1536
    monkeypatch.setattr(rag_service, "get_embedding", mock_get_embedding)
    
    # DB might have other chunks from other tests, so let's filter by a non-existent source
    results = rag_service.search(db_session, query="nothing", top_k=5, source_type="nonexistent")
    assert len(results) == 0

def test_mcp_discovery():
    import asyncio
    from app.mcp.server import mcp
    tools = asyncio.run(mcp.list_tools())
    tool_names = [t.name for t in tools]
    
    assert "get_candidate" in tool_names
    assert "get_job" in tool_names
    assert "search_knowledge" in tool_names
