import os
import sys
from sqlmodel import select, text

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine
from app.config import settings

def verify_connection():
    print(f"Testing connection to: {settings.DATABASE_URL.split('@')[-1]}") # Hide password
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Connection successful! Result:", result.scalar())
            
            # Check if tables exist
            result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            tables = [row[0] for row in result]
            print("Tables found:", tables)
            
            required_tables = ['users', 'folders', 'documents', 'document_chunks', 'chat_sessions', 'chat_messages']
            missing = [t for t in required_tables if t not in tables]
            
            if missing:
                print(f"WARNING: Missing tables: {missing}")
            else:
                print("All required tables are present.")
                
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_connection()
