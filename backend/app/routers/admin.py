import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth import get_current_user
from app.database import get_session
from app.models import (
    Document,
    DocumentChunk,
    ErrorLog,
    KnowledgeBase,
    TokenUsage,
    User,
    UserKnowledgeBaseLink,
    UserLog,
)
from app.services.rag import get_embedding

logger = logging.getLogger(__name__)

from app.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


# --- Dependencies ---
def get_admin_user(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


def censor_email(email: str) -> str:
    """Censor email for demo mode: user@domain.com -> u***@***.com"""
    if "@" in email:
        local, domain = email.split("@", 1)
        domain_suffix = domain.split(".")[-1] if "." in domain else domain
        return f"{local[0]}***@***.{domain_suffix}"
    return "***"


def check_demo_mode_mutation(admin: User = Depends(get_admin_user)):
    """Block mutations in PROD mode (demo mode)."""
    if settings.APP_MODE == "PROD":
        raise HTTPException(status_code=403, detail="Acción no autorizada en esta demo")
    return admin


# --- User Management ---
@router.get("/users")
def list_users(session: Session = Depends(get_session), admin: User = Depends(get_admin_user)):
    users = session.exec(select(User)).all()
    # Simple response model construction
    # Censor emails in PROD mode (demo mode)
    is_demo = settings.APP_MODE == "PROD"
    return [
        {
            "id": u.id,
            "email": censor_email(u.email) if is_demo else u.email,
            "role": u.role,
            "status": u.status,
            "knowledge_bases": [{"id": kb.id, "name": kb.name} for kb in u.knowledge_bases],
        }
        for u in users
    ]


class UpdateUserKBsRequest(BaseModel):
    kb_ids: list[int]


class UpdateUserRoleRequest(BaseModel):
    role: str  # 'user' or 'admin'


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    request: UpdateUserRoleRequest,
    session: Session = Depends(get_session),
    admin: User = Depends(check_demo_mode_mutation),
):
    if request.role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Allow self-demotion - frontend should handle session refresh
    is_self_change = user.id == admin.id

    user.role = request.role
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "email": user.email, "role": user.role, "self_changed": is_self_change}


@router.put("/users/{user_id}/knowledge_bases")
def update_user_kbs(
    user_id: int,
    request: UpdateUserKBsRequest,
    session: Session = Depends(get_session),
    admin: User = Depends(check_demo_mode_mutation),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Clear existing links
    existing_links = session.exec(select(UserKnowledgeBaseLink).where(UserKnowledgeBaseLink.user_id == user_id)).all()
    for link in existing_links:
        session.delete(link)

    # Add new links
    for kb_id in request.kb_ids:
        link = UserKnowledgeBaseLink(user_id=user_id, knowledge_base_id=kb_id)
        session.add(link)

    session.commit()
    return {"status": "updated"}


# --- Knowledge Base Management ---
@router.get("/knowledge_bases")
def list_kbs(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),  # Allow normal users to see? Or just admins? Admin for management.
):
    # Admins see all. Users might only need this if selecting where to upload?
    # For now, admin only for management.
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")

    try:
        kbs = session.exec(select(KnowledgeBase)).all()
        return [
            {
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "document_count": len(kb.documents),
                "is_default": kb.is_default,
            }
            for kb in kbs
        ]
    except Exception as e:
        logger.error(f"Error listing KBs: {e}")
        return []


class CreateKBRequest(BaseModel):
    name: str
    description: str | None = None
    is_default: bool = False


@router.post("/knowledge_bases")
def create_kb(
    request: CreateKBRequest, session: Session = Depends(get_session), admin: User = Depends(check_demo_mode_mutation)
):
    kb = KnowledgeBase(name=request.name, description=request.description, is_default=request.is_default)
    session.add(kb)
    session.commit()
    session.refresh(kb)
    return {"id": kb.id, "name": kb.name, "description": kb.description, "is_default": kb.is_default}


@router.patch("/knowledge_bases/{kb_id}/default")
def toggle_kb_default(kb_id: int, session: Session = Depends(get_session), admin: User = Depends(get_admin_user)):
    kb = session.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge Base not found")
    kb.is_default = not kb.is_default
    session.add(kb)
    session.commit()
    session.refresh(kb)
    return {"id": kb.id, "name": kb.name, "is_default": kb.is_default}


# --- Document Management (Admin) ---
@router.post("/documents/upload")
async def upload_document_to_kb(
    file: UploadFile = File(...),
    knowledge_base_id: int = Form(...),
    session: Session = Depends(get_session),
    admin: User = Depends(check_demo_mode_mutation),
):
    file_bytes = await file.read()
    filename = file.filename or "document"

    # Extract text based on file type
    if filename.lower().endswith(".pdf"):
        # Handle PDF files
        try:
            import io

            from PyPDF2 import PdfReader

            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            content = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n"
            if not content.strip():
                raise HTTPException(
                    status_code=400, detail="Could not extract text from PDF. The PDF might be scanned/image-based."
                )
        except ImportError:
            raise HTTPException(status_code=500, detail="PDF processing library not installed")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")
    else:
        # Handle text files (txt, md, etc.)
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content = file_bytes.decode("latin-1")
            except Exception:
                raise HTTPException(status_code=400, detail="Could not decode file. Please upload a text or PDF file.")

    # Create Doc
    doc = Document(
        title=filename,
        user_id=admin.id,
        knowledge_base_id=knowledge_base_id,
        type="pdf" if filename.lower().endswith(".pdf") else "text",
        path_url="uploaded_content",
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)

    # Chunk & Embed (500 char chunks)
    chunk_size = 500
    chunks = [content[i : i + chunk_size] for i in range(0, len(content), chunk_size)]

    for i, chunk_text in enumerate(chunks):
        if not chunk_text.strip():
            continue
        embedding = get_embedding(chunk_text[:1000])
        chunk = DocumentChunk(
            document_id=doc.id,
            content=chunk_text,
            embedding=embedding,
            chunk_index=i,
            chunk_metadata={"filename": filename},
        )
        session.add(chunk)

    session.commit()
    return {"status": "success", "doc_id": doc.id, "chunks_created": len(chunks)}


@router.get("/knowledge_bases/{kb_id}/documents")
def list_kb_documents(kb_id: int, session: Session = Depends(get_session), admin: User = Depends(get_admin_user)):
    docs = session.exec(select(Document).where(Document.knowledge_base_id == kb_id)).all()
    return [{"id": doc.id, "title": doc.title, "type": doc.type, "created_at": doc.created_at} for doc in docs]


@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: int, session: Session = Depends(get_session), admin: User = Depends(check_demo_mode_mutation)
):
    """Delete a document and all its associated chunks."""
    doc = session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete all chunks associated with this document first
    chunks = session.exec(select(DocumentChunk).where(DocumentChunk.document_id == doc_id)).all()
    for chunk in chunks:
        session.delete(chunk)

    # Delete the document
    session.delete(doc)
    session.commit()

    return {"status": "deleted", "doc_id": doc_id}


# --- System Logs ---


@router.get("/logs/users")
def get_user_layouts(limit: int = 100, session: Session = Depends(get_session), admin: User = Depends(get_admin_user)):
    """
    Get user logs including logins and token usage stats.
    We'll return a raw list of UserLog entries, plus we can augment or expect frontend to aggregate.
    Actually, let's just return the raw UserLogs for now.
    """
    logs = session.exec(select(UserLog).order_by(UserLog.created_at.desc()).limit(limit)).all()

    # Censor emails in PROD mode (demo mode)
    is_demo = settings.APP_MODE == "PROD"

    # Enrich with user email
    # A bit inefficient 1+N but okay for admin panel with small limits
    results = []
    for log in logs:
        user_email = log.user.email if log.user else "Unknown/Deleted"
        if is_demo and user_email not in ["Unknown/Deleted"]:
            user_email = censor_email(user_email)
        results.append(
            {
                "id": log.id,
                "user_email": user_email,
                "event": log.event,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
            }
        )

    # Also fetch recent Token Usage logs to mix in?
    # Or keep them separate. The request asked for "users and their token consumption".
    # Let's fetch TokenUsage rows too and format them similarly as "events".

    token_usages = session.exec(select(TokenUsage).order_by(TokenUsage.created_at.desc()).limit(limit)).all()
    for usage in token_usages:
        # manual join
        user = session.get(User, usage.user_id) if usage.user_id else None
        user_email = user.email if user else "System/Unknown"
        if is_demo and user_email not in ["System/Unknown"]:
            user_email = censor_email(user_email)

        results.append(
            {
                "id": f"tok_{usage.id}",
                "user_email": user_email,
                "event": "TOKEN_USAGE",
                "details": {"source": usage.source, "tokens": usage.tokens},
                "ip_address": None,
                "created_at": usage.created_at,
            }
        )

    # Sort combined by date desc
    results.sort(key=lambda x: x["created_at"], reverse=True)
    return results[:limit]


@router.get("/logs/errors")
def get_error_logs(limit: int = 100, session: Session = Depends(get_session), admin: User = Depends(get_admin_user)):
    """
    Get system error logs.
    """
    errors = session.exec(select(ErrorLog).order_by(ErrorLog.created_at.desc()).limit(limit)).all()

    # Security: Hide sensitive details if in PROD mode
    if settings.APP_MODE == "PROD":
        sanitized = []
        for e in errors:
            sanitized.append(
                {
                    "id": e.id,
                    "user_id": e.user_id,
                    "path": e.path,
                    "method": e.method,
                    "error_message": "Internal System Error (Hidden in PROD)",
                    "stack_trace": "Stack trace hidden in production mode for security.",
                    "created_at": e.created_at,
                }
            )
        return sanitized

    return errors
