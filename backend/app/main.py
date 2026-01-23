from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import init_db, get_session
from app.models import User, Conversation, Message, Document, DocumentChunk
from app.services.rag import rag_pipeline
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Init DB
    init_db()
    yield
    # Shutdown

app = FastAPI(title="Banking RAG API", lifespan=lifespan)

# --- Dependency Placeholder for Auth ---
# real implementation would verify JWT
def get_current_user(session: Session = Depends(get_session)):
    # For MVP/Dev, return the first user or raise
    # In production, use OAuth2PasswordBearer
    user = session.exec(select(User)).first()
    if not user:
        # Create default admin for dev if none exists
        user = User(email="admin@bank.com", hashed_password="hashed_secret")
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

@app.get("/")
def read_root():
    return {"message": "Banking RAG API is running"}

@app.post("/chat")
def chat_endpoint(query: str, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    """
    RAG Chat Endpoint:
    1. Retrieve relevant docs (Voyage + PGVector)
    2. Rerank them
    3. Generate response (LLM - to be implemented/connected)
    """
    
    # 1. RAG Retrieve
    context_chunks = rag_pipeline(session, query, user.id)
    
    # 2. Get/Create Conversation (moved up for history access)
    conv = session.exec(select(Conversation).where(Conversation.user_id == user.id).where(Conversation.title == "General")).first()
    if not conv:
        conv = Conversation(user_id=user.id, title="General")
        session.add(conv)
        session.commit()
        session.refresh(conv)
        
    # Get History (Last 5 messages)
    history = session.exec(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at.desc())
        .limit(5)
    ).all()
    history = list(reversed(history)) # Oldest first

    # 3. LLM Generation (Groq + Tavily)
    from app.services.llm import generate_response
    
    llm_result = generate_response(query, context_chunks, history)
    response_text = llm_result["response"]
    
    # 4. Save History    
    session.add(Message(conversation_id=conv.id, role="user", content=query))
    session.add(Message(conversation_id=conv.id, role="assistant", content=response_text))
    session.commit()
    
    return {
        "response": response_text,
        "sources": llm_result["sources"]
    }

@app.post("/upload")
def upload_document(file_name: str, content: str, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    """Mock Upload Endpoint."""
    # 1. Create Document
    doc = Document(filename=file_name, user_id=user.id)
    session.add(doc)
    session.commit()
    session.refresh(doc)
    
    # 2. Chunk & Embed (Mock call to rag service embed)
    # real: embeddings = get_embedding(content)
    # For now, we assume rag service works
    from app.services.rag import get_embedding
    
    embedding = get_embedding(content[:500]) # Embed first 500 chars as mock of chunking
    
    chunk = DocumentChunk(document_id=doc.id, content=content, embedding=embedding)
    session.add(chunk)
    session.commit()
    
    return {"status": "success", "doc_id": doc.id}
