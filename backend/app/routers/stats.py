from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.database import get_session
from app.models import User, Document, ChatMessage
from app.auth import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/overview")
def get_overview_stats(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """
    Returns system statistics for the dashboard.
    Only allows access if user is authenticated (checking role in frontend for display logic).
    """
    
    # Counts
    # Docs
    docs_count = session.exec(select(func.count(Document.id))).one()
    
    # Users (Total)
    users_count = session.exec(select(func.count(User.id))).one()
    
    # Queries (Total user messages)
    queries_count = session.exec(select(func.count(ChatMessage.id)).where(ChatMessage.role == "user")).one()
    
    return {
        "documents": docs_count,
        "users": users_count,
        "queries": queries_count
    }

@router.get("/activity")
def get_activity_stats(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """
    Returns query activity for the last 24 hours (grouped by hour).
    """
    from sqlalchemy import text
    
    # Raw SQL for time bucketing (simplest for now with SQLite/Postgres differences, assuming Postgres)
    # If using SQLite dev, this might fail with date_trunc.
    # Let's assume Postgres as per user metadata (pgvector).
    
    query = text("""
        SELECT 
            date_trunc('hour', created_at) as hour,
            count(*) as count
        FROM chat_messages
        WHERE role = 'user' AND created_at > now() - interval '24 hours'
        GROUP BY hour
        ORDER BY hour ASC
    """)
    
    try:
        results = session.exec(query).all()
        # Format for frontend: labels (hour), data (count)
        data = [{"hour": row[0].strftime("%H:%M"), "count": row[1]} for row in results]
        return data
    except Exception as e:
        print(f"Stats Error: {e}")
        return []
