import logging
import os
import random

import voyageai
from sqlmodel import Session, select

from app.models import Document, DocumentChunk, User, UserKnowledgeBaseLink

logger = logging.getLogger(__name__)

# --- Embeddings ---
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
vo_client = voyageai.Client(api_key=VOYAGE_API_KEY) if VOYAGE_API_KEY else None


def get_embedding(text: str) -> list[float]:
    """Generates embedding using Voyage AI (model=voyage-2, dim=1024)."""
    if vo_client:
        try:
            # voyage-2 is 1024 dimensions.
            result = vo_client.embed([text], model="voyage-2", input_type="document").embeddings[0]
            return result
        except Exception as e:
            logger.error(f"Voyage Error: {e}")
            # Fallback mock for dev if API fails
            return [0.0] * 1024

    # Mock for local dev without key
    return [random.uniform(-0.1, 0.1) for _ in range(1024)]


def rerank_documents(query: str, chunks: list[DocumentChunk], top_k: int = 5) -> list[DocumentChunk]:
    """Mock Reranker for MVP - just return top K from vector search."""
    # In production, use vo_client.rerank(...)
    return chunks[:top_k]


def vector_search(session: Session, query: str, user_id: int, limit: int = 20) -> list[DocumentChunk]:
    """
    Perform vector search filtered by User's assigned Knowledge Bases.
    """
    # 1. Get User's Knowledge Bases
    # Optimization: Could cache this or pass it in.
    user = session.get(User, user_id)
    if not user:
        return []

    # Get IDs of KBs assigned to user
    # If admin, maybe search all? No, behave like user for chat.
    # explicit link check
    kb_links = session.exec(select(UserKnowledgeBaseLink).where(UserKnowledgeBaseLink.user_id == user_id)).all()
    kb_ids = [link.knowledge_base_id for link in kb_links]

    # If no KBs assigned, return empty (or default public ones?)
    # Let's say if no KBs assigned, they see nothing.
    if not kb_ids:
        # Check for 'default' global KBs if any
        # defaults = session.exec(select(KnowledgeBase).where(KnowledgeBase.is_default == True)).all()
        # kb_ids = [kb.id for kb in defaults]
        if not kb_ids:
            return []

    # 2. Generate query embedding
    query_embedding = get_embedding(query)

    # 3. SQLModel Query with PGVector & Filtering
    # Join filtered by KB IDs
    statement = (
        select(DocumentChunk)
        .join(Document)
        .where(Document.knowledge_base_id.in_(kb_ids))
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )

    results = session.exec(statement).all()
    return list(results)


def rag_pipeline(session: Session, query: str, user_id: int) -> list[DocumentChunk]:
    """Full RAG Pipeline: Retrieval + Reranking."""
    # 1. Retrieve candidates
    candidates = vector_search(session, query, user_id, limit=20)

    # 2. Rerank
    final_results = rerank_documents(query, candidates, top_k=5)

    return final_results
