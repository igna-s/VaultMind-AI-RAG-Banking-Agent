from sqlmodel import Session, select
from app.database import engine
from sqlalchemy import text
from datetime import datetime, timedelta
from collections import defaultdict
import logging

# Mock logger
logger = logging.getLogger(__name__)

def debug_stats():
    with Session(engine) as session:
        print("--- Debugging Stats Logic ---")
        
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
                
                groq_val = hourly_data.get(hour_key, {}).get("groq", 0)
                retriever_val = hourly_data.get(hour_key, {}).get("retriever", 0)
                
                if groq_val > 0 or retriever_val > 0:
                    print(f"MATCH FOUND at {hour_key}: Groq={groq_val}, Retriever={retriever_val}")
                    
                data.append({
                    "hour": hour_key,
                    "groq": groq_val,
                    "retriever": retriever_val
                })
        except Exception as e:
                print(f"Error executing query: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    debug_stats()
