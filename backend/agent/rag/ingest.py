import os
import shutil
from typing import List, Optional
from langchain_postgres import PGVector
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings # User uses Groq usually, but embeddings... Groq doesn't provide embeddings natively via API mostly? 
# Usually people use OpenAI or HuggingFace for embeddings.
# Let's check environment... User has OpenAI key? 
# The requirements had langchain-openai.
# But user said "usa groq en vez de openai".
# For embeddings, Groq doesn't have an endpoint typically.
# We will use HuggingFace (free/local) or check if keys exist.
# Let's assume standard OpenAI embeddings if key present, else HuggingFace.
from langchain_huggingface import HuggingFaceEmbeddings

from agent.db import get_db_url, get_session, UserFile

# 300MB Limit in bytes
MAX_SIZE_BYTES = 300 * 1024 * 1024 

def get_embeddings():
    # Fallback to local HF if no OpenAI key, or prefer free if standard
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def check_user_storage_limit(user_id: str, new_file_size: int) -> bool:
    session = get_session()
    total_size = 0
    # Sum sizes of existing files for user
    # Simplified query
    files = session.query(UserFile).filter(UserFile.user_id == user_id).all()
    total_size = sum(f.size_mb * 1024 * 1024 for f in files)
    
    if total_size + new_file_size > MAX_SIZE_BYTES:
        return False
    return True

def ingest_file(file_path: str, user_id: str, file_type: str = "temp", session_id: Optional[str] = None) -> str:
    """Ingest a file into the RAG system."""
    
    # 1. Check size
    file_size = os.path.getsize(file_path)
    if not check_user_storage_limit(user_id, file_size):
        return "Error: Storage limit of 300MB exceeded."

    # 2. Read content (Text/PDF)
    # Simplified text reading for now
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception as e:
        return f"Error reading file: {e}"

    # 3. Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    metadata = {"source": file_path, "user_id": user_id, "type": file_type}
    if session_id:
        metadata["session_id"] = session_id
        
    docs = text_splitter.create_documents([text], metadatas=[metadata])
    
    # 4. Store in DB Metadata
    session = get_session()
    new_file = UserFile(
        filename=os.path.basename(file_path),
        file_type=file_type,
        file_path=file_path,
        user_id=user_id,
        size_mb=int(file_size / (1024*1024))
        # We should add session_id column to DB too if we want to query it SQL-side, 
        # but for now vector store metadata is enough for RAG.
    )
    session.add(new_file)
    session.commit()

    # 5. Store in Vector DB
    connection_string = get_db_url()
    vector_store = PGVector(
        embeddings=get_embeddings(),
        collection_name="rag_documents",
        connection=connection_string,
        use_jsonb=True,
    )
    
    vector_store.add_documents(docs)
    
    return f"Successfully ingested {os.path.basename(file_path)} as {file_type}."
