import os
import voyageai
from sqlmodel import Session, select
from app.models import DocumentChunk, Document
from sqlalchemy import func

# Initialize Voyage Client
# Ensure VOYAGE_API_KEY is set in .env
voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

EMBEDDING_MODEL = "voyage-3-lite"
RERANK_MODEL = "rerank-2-lite"

def get_embedding(text: str) -> list[float]:
    """Generate embedding for a single text."""
    # embed returns a list of embeddings items
    result = voyage_client.embed([text], model=EMBEDDING_MODEL, input_type="document")
    return result.embeddings[0]

def rerank_documents(query: str, chunks: list[DocumentChunk], top_k: int = 5) -> list[DocumentChunk]:
    """Rerank retrieved chunks using Voyage Reranker."""
    if not chunks:
        return []
    
    documents_content = [chunk.content for chunk in chunks]
    reranking = voyage_client.rerank(
        query=query,
        documents=documents_content,
        model=RERANK_MODEL,
        top_k=top_k
    )
    
    # RerankingResult object contains results with index and relevance_score
    reranked_chunks = []
    for r in reranking.results:
        # r.index corresponds to the index in the input list
        chunk = chunks[r.index]
        # We could attach score if needed: chunk.score = r.relevance_score
        reranked_chunks.append(chunk)
        
    return reranked_chunks

def vector_search(session: Session, query: str, user_id: int, limit: int = 20) -> list[DocumentChunk]:
    """Perform hybrid search: Filter by User -> Vector Sim -> optional: hybrid keyword?"""
    
    # 1. Generate query embedding
    query_embedding = voyage_client.embed([query], model=EMBEDDING_MODEL, input_type="query").embeddings[0]
    
    # 2. SQLModel Query with PGVector
    # Filter by Join with Document to check user_id
    statement = (
        select(DocumentChunk)
        .join(Document)
        .where(Document.user_id == user_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    
    results = session.exec(statement).all()
    return list(results)

def rag_pipeline(session: Session, query: str, user_id: int) -> list[DocumentChunk]:
    """Full RAG Pipeline: Retrieval + Reranking."""
    # 1. Retrieve candidates (Broad search, e.g. top 20-30)
    candidates = vector_search(session, query, user_id, limit=30)
    
    # 2. Rerank (Refine to top 5)
    final_results = rerank_documents(query, candidates, top_k=5)
    
    return final_results
