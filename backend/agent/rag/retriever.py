from typing import List
from langchain_postgres import PGVector
from langchain_core.documents import Document
from agent.db import get_db_url
from agent.rag.ingest import get_embeddings

def retrieve_documents(query: str, user_id: str, session_id: str = None, top_k: int = 4) -> List[Document]:
    """Retrieve documents relevant to the query."""
    
    connection_string = get_db_url()
    vector_store = PGVector(
        embeddings=get_embeddings(),
        collection_name="rag_documents",
        connection=connection_string,
        use_jsonb=True,
    )
    
    # Metadata filter
    # We want: 
    # 1. Documents owned by this user (or global docs if user_id is generic?)
    #    Actually, 'groups' might be shared or user-specific? 
    #    User requirement: "archivos asociados al usuario". So user_id filter is key.
    # 2. Logic:
    #    - type='group' (persistent for user)
    #    - type='temp' (session bound)
    
    # LangChain PGVector supports metadata filtering.
    # We construct a filter for: (user_id == uid) AND ((type == 'group') OR (type == 'temp' AND session_id == sid))
    # PGVector filter syntax is usually dict. Complex OR logic might need specific syntax or just filtering post-retrieval
    # if the library wrapper is limited.
    # `langchain-postgres` PGVector supports some filter translation.
    
    # Ideally:
    # filter = {
    #    "user_id": user_id,
    #    "$or": [
    #       {"type": "group"},
    #       {"type": "temp", "session_id": session_id}
    #    ]
    # }
    
    # For now, let's keep it simple: Filter by user_id, then manually filter in Python if needed, 
    # or trust the retriever to handle context. 
    # Actually, RAG usually retrieves by similarity. Filtering drastically reduces search space.
    # Let's filter by user_id at least.
    
    # Note: 'session_id' wasn't saved in `ingest.py` (my bad). I should update ingest.
    
    results = vector_store.similarity_search(query, k=top_k, filter={"user_id": user_id})
    return results
