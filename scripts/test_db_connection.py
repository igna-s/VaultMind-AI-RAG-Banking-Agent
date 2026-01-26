import sys
import os
# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.database import engine
from sqlalchemy import text
from app.config import settings

print(f"Testing connection to: {settings.DATABASE_URL}")

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Connection successful!", result.scalar())
except Exception as e:
    print(f"Connection failed: {e}")
