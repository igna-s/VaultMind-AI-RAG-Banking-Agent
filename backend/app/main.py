from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import init_db, get_session, engine
from app.models import User, ChatSession, ChatMessage, Document, DocumentChunk, Folder
from app.services.rag import rag_pipeline, get_embedding
from app.routers.auth import router as auth_router
from app.auth import get_current_user, get_password_hash
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
from fastapi import Request

# --- Pydantic Schemas for Request/Response ---
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    session_id: int

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Init DB
    init_db()
    
    # Create default admin if not exists
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == "admin@bank.com")).first()
        if not user:
            # Create default admin with hashed password
            user = User(
                email="admin@bank.com", 
                hashed_password=get_password_hash("password"), 
                status="active", 
                role="admin"
            )
            session.add(user)
            session.commit()
            
    yield
    # Shutdown

app = FastAPI(title="Banking RAG API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from fastapi.middleware.cors import CORSMiddleware

# CORS Configuration - MUST be added before routers
origins = [
    "http://localhost:5173", # Vite Dev Server
    "http://localhost:4173", # Vite Preview
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

# User dependency imported from app.auth

def get_admin_user(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

@app.get("/admin/users")
def list_users(admin: User = Depends(get_admin_user), session: Session = Depends(get_session)):
    """Admin only: List all users"""
    return session.exec(select(User)).all()

@app.get("/")
def read_root():
    return {"message": "Banking RAG API is running with PostgreSQL + pgvector"}

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
def chat_endpoint(
    request: Request,
    chat_request: ChatRequest, 
    session: Session = Depends(get_session), 
    user: User = Depends(get_current_user)
):
    """
    RAG Chat Endpoint:
    1. Retrieve relevant docs (PGVector)
    2. Rerank them
    3. Generate response (LLM)
    4. Store history
    """
    
    # 1. RAG Retrieve
    context_chunks = rag_pipeline(session, chat_request.query, user.id)
    
    # 2. Get/Create ChatSession
    chat_session = None
    if chat_request.session_id:
        chat_session = session.get(ChatSession, chat_request.session_id)
        if not chat_session or chat_session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Find 'General' or create new
        chat_session = session.exec(
            select(ChatSession).where(ChatSession.user_id == user.id).where(ChatSession.title == "General")
        ).first()
        if not chat_session:
            chat_session = ChatSession(user_id=user.id, title="General")
            session.add(chat_session)
            session.commit()
            session.refresh(chat_session)
            
    # Get History (Last 5 messages)
    history = session.exec(
        select(ChatMessage)
        .where(ChatMessage.session_id == chat_session.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(5)
    ).all()
    history = list(reversed(history)) # Oldest first

    # 3. LLM Generation
    from app.services.llm import generate_response
    
    llm_result = generate_response(chat_request.query, context_chunks, history)
    response_text = llm_result["response"]
    
    # Extract sources for storage
    used_sources_meta = []
    if context_chunks:
        for chunk in context_chunks:
            meta = {
                "doc_id": chunk.document_id,
                "filename": chunk.document.title if chunk.document else "unknown",
                "chunk_id": chunk.id
            }
            used_sources_meta.append(meta)
            
    # 4. Save History    
    # User message
    user_msg = ChatMessage(session_id=chat_session.id, role="user", content=chat_request.query)
    session.add(user_msg)
    
    # AI message
    ai_msg = ChatMessage(
        session_id=chat_session.id, 
        role="ai", 
        content=response_text,
        used_sources=used_sources_meta
    )
    session.add(ai_msg)
    session.commit()
    
    return {
        "response": response_text,
        "sources": llm_result["sources"],
        "session_id": chat_session.id
    }

@app.post("/upload")
def upload_document(
    title: str, 
    content: str, 
    folder_id: Optional[int] = None,
    session: Session = Depends(get_session), 
    user: User = Depends(get_current_user)
):
    """
    Upload and vectorize a document.
    """
    # 1. Create Document
    doc = Document(
        title=title, 
        user_id=user.id, 
        folder_id=folder_id,
        type="text",
        path_url="uploaded_content"
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    
    # 2. Chunk & Embed (Mock chunking for MVP)
    # In real app: split text by tokens/paragraphs
    
    # Mock embedding generator (must match 1536 dim)
    # Using first 500 chars to represent chunk
    embedding = get_embedding(content[:500]) 
    
    chunk = DocumentChunk(
        document_id=doc.id, 
        content=content, 
        embedding=embedding,
        chunk_index=0,
        chunk_metadata={"author": "user_upload"}
    )
    session.add(chunk)
    session.commit()
    
    return {"status": "success", "doc_id": doc.id}
