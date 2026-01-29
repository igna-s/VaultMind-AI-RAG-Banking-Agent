from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Dict, Any
from app.database import get_session
from app.models import User, ChatSession, ChatMessage
from app.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/sessions")
def get_user_sessions(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """List all chat sessions for the current user."""
    sessions = session.exec(
        select(ChatSession)
        .where(ChatSession.user_id == user.id)
        .order_by(ChatSession.updated_at.desc())
    ).all()
    
    return [
        {
            "id": s.id,
            "title": s.title,
            "date": s.updated_at.strftime("%Y-%m-%d %H:%M"),
            "timestamp": s.updated_at
        }
        for s in sessions
    ]

@router.get("/sessions/{session_id}")
def get_session_history(
    session_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Get message history for a specific session."""
    chat_session = session.get(ChatSession, session_id)
    if not chat_session or chat_session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
        
    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    ).all()
    
    return {
        "id": chat_session.id,
        "title": chat_session.title,
        "messages": [
            {
                "id": m.id,
                "text": m.content,
                "sender": m.role, # 'user' or 'ai'
                "timestamp": m.created_at,
                "steps": m.reasoning_data.get("steps", []) if m.reasoning_data else [],
                "status": None # Clear status for history so text is shown
            }
            for m in messages
        ]
    }
