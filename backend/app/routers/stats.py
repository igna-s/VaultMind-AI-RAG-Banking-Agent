from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.database import get_session
from app.models import User, Document, ChatMessage, TokenUsage
from app.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

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
    Always returns 24 data points (one per hour).
    """
    from sqlalchemy import text
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    # Calculate cutoff in Python to ensure consistent timezone handling (UTC)
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=24)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")

    query = text(f"""
        SELECT 
            date_trunc('hour', hour) as bucket,
            source,
            SUM(tokens) as total_tokens
        FROM token_usage
        WHERE hour >= '{cutoff_str}'
        GROUP BY bucket, source
        ORDER BY bucket ASC
    """)
    
    try:
        # Use session.execute() for raw SQL (not session.exec())
        result = session.execute(query)
        rows = result.fetchall()
        
        # Build hourly map from DB results
        hourly_data = defaultdict(lambda: {"groq": 0, "retriever": 0})
        
        for row in rows:
            # Row[0] is a datetime object from date_trunc
            if row[0]:
                hour_str = row[0].strftime("%H:00")
                source = row[1]
                tokens = int(row[2]) if row[2] else 0
                hourly_data[hour_str][source] = tokens
        
        # Generate 24 data points (one for each hour in the last 24h)
        # We recalculate 'now' to match the exact same loop logic
        data = []
        for i in range(24):
            hour_offset = 23 - i  # Start from 24h ago to now
            hour_time = now - timedelta(hours=hour_offset)
            hour_key = hour_time.strftime("%H:00")
            
            data.append({
                "hour": hour_key,
                "groq": hourly_data.get(hour_key, {}).get("groq", 0),
                "retriever": hourly_data.get(hour_key, {}).get("retriever", 0)
            })
        
        return data
        
    except Exception as e:
        logger.error(f"Stats Error: {e}")
        import traceback
        traceback.print_exc()
        # Return empty 24-hour array on error
        return [{"hour": f"{i:02d}:00", "groq": 0, "retriever": 0} for i in range(24)]

