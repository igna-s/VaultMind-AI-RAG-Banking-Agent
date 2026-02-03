from sqlmodel import Session, select, func
from app.database import engine
from app.models import TokenUsage
from sqlalchemy import text

def check_sources():
    with Session(engine) as session:
        # Count by source
        query = text("SELECT source, COUNT(*), SUM(tokens) FROM token_usage GROUP BY source")
        result = session.execute(query).fetchall()
        
        print("--- Token Usage by Source ---")
        for row in result:
            print(f"Source: {row[0]}, Count: {row[1]}, Total Tokens: {row[2]}")
            
if __name__ == "__main__":
    check_sources()
