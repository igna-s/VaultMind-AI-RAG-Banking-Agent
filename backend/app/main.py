import logging
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
from contextlib import asynccontextmanager
from typing import Any

from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session, select

from app.auth import get_current_user, get_password_hash
from app.config import settings
from app.database import engine, get_session, init_db
from app.limiter import limiter
from app.models import ChatMessage, ChatSession, Document, DocumentChunk, ErrorLog, User
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.stats import router as stats_router
from app.services.rag import get_embedding, rag_pipeline


# --- Pydantic Schemas for Request/Response ---
class ChatRequest(BaseModel):
    query: str
    session_id: int | None = None


class ChatResponse(BaseModel):
    response: str
    sources: list[str]
    session_id: int
    reasoning_data: dict[str, Any] | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Init DB
    try:
        init_db()
    except Exception as e:
        logger.critical(f"CRITICAL DATABASE ERROR: Failed to initialize database on startup: {e}")
        # logging error but not raising, to allow app to start for debugging
        pass

    # Create default admin if not exists
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == "admin@bank.com")).first()
        if not user:
            # Create default admin with hashed password
            user = User(
                email="admin@bank.com",
                hashed_password=get_password_hash("password"),  # TODO: Use env var for initial admin password
                status="active",
                role="admin",
            )
            session.add(user)
            session.commit()

    yield
    # Shutdown


app = FastAPI(title="Banking RAG API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback

    logger.error(f"GLOBAL 500 ERROR: {exc}")
    # traceback.print_exc() # Optional: keep or remove depending on logger config. Let's keep it but via logger usually better.
    # For now just cleaning `print`.
    traceback.print_exc()

    # Save ErrorLog
    try:
        # Try to get user from request state if available (custom middleware might set it)
        # Or simple heuristic if we had auth middleware covering everything.
        # Since Depends(get_current_user) runs in router, we might not have it here easily for all crashes.
        # But we can capture path/method.

        with Session(engine) as session:
            error_log = ErrorLog(
                path=str(request.url), method=request.method, error_message=str(exc), stack_trace=traceback.format_exc()
            )
            session.add(error_log)
            session.commit()
    except Exception as db_e:
        logger.error(f"Failed to save ErrorLog: {db_e}")

    # Return generic error in PROD
    error_detail = str(exc)
    if settings.APP_MODE == "PROD":
        error_detail = "An internal error occurred."

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": error_detail},
    )


from fastapi.middleware.cors import CORSMiddleware

# CORS Configuration - MUST be added before routers
# TODO: Move these to .env for production
# CORS Configuration - MUST be added before routers
origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Essential for cookies
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour to reduce latency
)

app.include_router(auth_router)
app.include_router(stats_router)
app.include_router(chat_router)
app.include_router(admin_router)

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


import json

from fastapi.responses import StreamingResponse


@app.post("/chat")
@limiter.limit("30/minute")
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    RAG Chat Endpoint (Streaming Status):
    1. Retrieve relevant docs (PGVector)
    2. Rerank them
    3. Generate response (LLM Loop with Streaming)
    4. Store history
    """

    async def event_generator():
        try:
            # 1. RAG Retrieve
            yield json.dumps({"type": "status", "content": "Retrieving context..."}) + "\n"
            context_chunks = rag_pipeline(session, chat_request.query, user.id)

            # 2. Get/Create ChatSession
            chat_session = None
            if chat_request.session_id:
                chat_session = session.get(ChatSession, chat_request.session_id)
                if not chat_session or chat_session.user_id != user.id:
                    yield json.dumps({"type": "error", "content": "Session not found"}) + "\n"
                    return
            else:
                # Create NEW session with title from query
                title = chat_request.query[:30] + "..." if len(chat_request.query) > 30 else chat_request.query
                chat_session = ChatSession(user_id=user.id, title=title)
                session.add(chat_session)
                session.commit()
                session.refresh(chat_session)

            # Update timestamp
            chat_session.updated_at = datetime.utcnow()
            session.add(chat_session)
            session.commit()

            # Get History (Last 5 messages)
            history = session.exec(
                select(ChatMessage)
                .where(ChatMessage.session_id == chat_session.id)
                .order_by(ChatMessage.created_at.desc())
                .limit(5)
            ).all()
            history = list(reversed(history))  # Oldest first

            # 3. LLM Generation (Deep Agent Loop)
            from app.services.llm import generate_response_stream

            final_result_payload = None

            async for event in generate_response_stream(chat_request.query, context_chunks, history, user_id=user.id):
                if event["type"] == "status":
                    yield json.dumps(event) + "\n"
                elif event["type"] == "answer" or event["type"] == "result":
                    final_result_payload = event
                elif event["type"] == "error":
                    yield json.dumps(event) + "\n"
                    return

            if not final_result_payload:
                yield json.dumps({"type": "error", "content": "No response generated"}) + "\n"
                return

            response_text = final_result_payload["response"]
            reasoning_data = final_result_payload["reasoning_data"]
            sources = final_result_payload["sources"]

            # Extract sources for storage
            used_sources_meta = []
            if context_chunks:
                for chunk in context_chunks:
                    meta = {
                        "doc_id": chunk.document_id,
                        "filename": chunk.document.title if chunk.document else "unknown",
                        "chunk_id": chunk.id,
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
                used_sources=used_sources_meta,
                reasoning_data=reasoning_data,
            )
            session.add(ai_msg)
            session.commit()

            # Yield Final Answer
            yield (
                json.dumps(
                    {
                        "type": "answer",
                        "response": response_text,
                        "sources": sources,
                        "session_id": chat_session.id,
                        "reasoning_data": reasoning_data,
                    }
                )
                + "\n"
            )
        except Exception as e:
            import traceback

            logger.error(f"Chat endpoint error: {e}")
            traceback.print_exc()

            # Save to ErrorLog for debugging in PROD
            try:
                with Session(engine) as err_session:
                    error_log = ErrorLog(
                        path="chat_stream",
                        method="STREAM",
                        error_message=str(e),
                        stack_trace=traceback.format_exc(),
                        user_id=user.id,
                    )
                    err_session.add(error_log)
                    err_session.commit()
            except Exception as db_e:
                logger.error(f"Failed to save chat ErrorLog: {db_e}")

            error_msg = f"Server error: {str(e)}"
            if settings.APP_MODE == "PROD":
                error_msg = "An unexpected error occurred. Please try again later."

            yield json.dumps({"type": "error", "content": error_msg}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


@app.post("/upload")
def upload_document(
    title: str,
    content: str,
    folder_id: int | None = None,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Upload and vectorize a document.
    """
    # 1. Create Document
    doc = Document(title=title, user_id=user.id, folder_id=folder_id, type="text", path_url="uploaded_content")
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
        chunk_metadata={"author": "user_upload"},
    )
    session.add(chunk)
    session.commit()

    return {"status": "success", "doc_id": doc.id}
