from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.database import get_session
from app.models import User, Document, ChatMessage, TokenUsage
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
    Returns token usage for the last 24 hours (grouped by hour).
    Returns separate data for 'groq' (LLM) and 'retriever' (embeddings).
    """
    from sqlalchemy import text
    
    query = text("""
        SELECT 
            date_trunc('hour', hour) as bucket,
            source,
            SUM(tokens) as total_tokens
        FROM token_usage
        WHERE hour > now() - interval '24 hours'
        GROUP BY bucket, source
        ORDER BY bucket ASC
    """)
    
    try:
        results = session.exec(query).all()
        # Build response: [{hour: "10:00", groq: 1500, retriever: 200}, ...]
        from collections import defaultdict
        hourly_data = defaultdict(lambda: {"groq": 0, "retriever": 0})
        
        for row in results:
            hour_str = row[0].strftime("%H:%M")
            source = row[1]
            tokens = row[2]
            hourly_data[hour_str][source] = tokens
        
        # Convert to array format for frontend
        data = [{"hour": h, "groq": v["groq"], "retriever": v["retriever"]} for h, v in sorted(hourly_data.items())]
        return data
    except Exception as e:
        print(f"Stats Error: {e}")
        return []
