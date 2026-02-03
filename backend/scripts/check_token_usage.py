from sqlmodel import Session, select
from app.database import engine
from app.models import TokenUsage
from datetime import datetime, timedelta

def check_token_usage():
    with Session(engine) as session:
        # Check all records
        all_records = session.exec(select(TokenUsage)).all()
        print(f"Total TokenUsage records: {len(all_records)}")
        
        # Check records in last 24h
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_records = session.exec(select(TokenUsage).where(TokenUsage.hour >= cutoff)).all()
        print(f"TokenUsage records in last 24h: {len(recent_records)}")
        
        if recent_records:
            print("Sample recent records:")
            for r in recent_records[:5]:
                print(f"Time: {r.hour}, Source: {r.source}, Tokens: {r.tokens}, UserID: {r.user_id}")
        else:
            print("No recent records found.")
            
        # Check if any records exist at all
        if all_records and not recent_records:
            print(f"Latest record time: {all_records[-1].hour}")

if __name__ == "__main__":
    check_token_usage()
