from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session, select
from app.database import get_session
from app.models import User, KnowledgeBase, Document, UserKnowledgeBaseLink, DocumentChunk
from app.auth import get_current_user
from app.services.rag import get_embedding

router = APIRouter(prefix="/admin", tags=["admin"])

# --- Dependencies ---
def get_admin_user(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

# --- User Management ---
@router.get("/users")
def list_users(
    session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user)
):
    users = session.exec(select(User)).all()
    # Simple response model construction
    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "status": u.status,
            "knowledge_bases": [
                {"id": kb.id, "name": kb.name} for kb in u.knowledge_bases
            ]
        }
        for u in users
    ]

@router.put("/users/{user_id}/knowledge_bases")
def update_user_kbs(
    user_id: int,
    kb_ids: List[int],
    session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Clear existing links
    # This is rough, ideally we sync
    existing_links = session.exec(select(UserKnowledgeBaseLink).where(UserKnowledgeBaseLink.user_id == user_id)).all()
    for link in existing_links:
        session.delete(link)
    
    # Add new links
    for kb_id in kb_ids:
        link = UserKnowledgeBaseLink(user_id=user_id, knowledge_base_id=kb_id)
        session.add(link)
    
    session.commit()
    return {"status": "updated"}

# --- Knowledge Base Management ---
@router.get("/knowledge_bases")
def list_kbs(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user) # Allow normal users to see? Or just admins? Admin for management.
):
    # Admins see all. Users might only need this if selecting where to upload? 
    # For now, admin only for management.
    if user.role != 'admin':
         raise HTTPException(status_code=403, detail="Admin privileges required")

    try:
        kbs = session.exec(select(KnowledgeBase)).all()
        return [
            {
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "document_count": len(kb.documents)
            }
            for kb in kbs
        ]
    except Exception as e:
        print(f"Error listing KBs: {e}")
        return []

@router.post("/knowledge_bases")
def create_kb(
    name: str,
    description: Optional[str] = None,
    session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user)
):
    kb = KnowledgeBase(name=name, description=description)
    session.add(kb)
    session.commit()
    return kb

# --- Document Management (Admin) ---
@router.post("/documents/upload")
async def upload_document_to_kb(
    file: UploadFile = File(...),
    knowledge_base_id: int = Form(...),
    session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user)
):
    content = (await file.read()).decode("utf-8") # Text files only for MVP
    
    # Create Doc
    doc = Document(
        title=file.filename,
        user_id=admin.id, # Uploaded by admin
        knowledge_base_id=knowledge_base_id,
        type="text",
        path_url="uploaded_content"
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    
    # Chunk & Embed (MVP: single chunk or simplistic split)
    # 500 char chunks
    chunk_size = 500
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    for i, chunk_text in enumerate(chunks):
        embedding = get_embedding(chunk_text[:1000]) # Embed
        chunk = DocumentChunk(
            document_id=doc.id,
            content=chunk_text,
            embedding=embedding,
            chunk_index=i,
            chunk_metadata={"filename": file.filename}
        )
        session.add(chunk)
    
    session.commit()
    return {"status": "success", "doc_id": doc.id}

@router.get("/knowledge_bases/{kb_id}/documents")
def list_kb_documents(
    kb_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(get_admin_user)
):
    docs = session.exec(select(Document).where(Document.knowledge_base_id == kb_id)).all()
    return docs
