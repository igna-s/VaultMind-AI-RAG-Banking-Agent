import sys
import os
# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.database import engine
from app.models import User
from sqlmodel import Session, select
from app.config import settings

print(f"Connecting to: {settings.DATABASE_URL}")

try:
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"- {user.email} (Role: {user.role}, Status: {user.status})")
except Exception as e:
    print(f"Query failed: {e}")
