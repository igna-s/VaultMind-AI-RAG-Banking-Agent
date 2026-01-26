import os
import sys
from sqlalchemy import text

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine

def reset_database():
    print("⚠️  WARNING: This will DROP ALL TABLES in the database!")
    print(f"Target Database: {engine.url.database}")
    print("Host: ", engine.url.host)
    
    # Confirmation mechanism skipped for script, but would be good in CLI
    print("🚀 Dropping all tables...")
    
    try:
        with engine.connect() as connection:
            # Drop tables in specific order to avoid foreign key constraints issues
            # Or just use CASCADE
            
            # The list of tables to drop (Legacy + New)
            tables_to_drop = [
                'document_chunks', 
                'documents', 
                'folders', 
                'chat_messages', 
                'chat_sessions', 
                'users',
                # Legacy tables identified
                'conversations', 
                'messages', 
                'user_files' 
            ]
            
            for table in tables_to_drop:
                print(f"   Dropping table: {table} ...")
                connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            
            connection.commit()
            print("✅ All tables dropped successfully.")
            
    except Exception as e:
        print(f"❌ Error during reset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
