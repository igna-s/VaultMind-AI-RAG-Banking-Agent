import os
import sys
from sqlalchemy import text

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine

def check_indexes():
    print("🔍 Checking indexes on 'document_chunks'...")
    
    try:
        with engine.connect() as connection:
            # Query pg_indexes to see all indexes on the table
            query = text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'document_chunks';
            """)
            
            result = connection.execute(query)
            indexes = result.fetchall()
            
            hnsw_found = False
            for name, def_ in indexes:
                print(f"   - {name}")
                if 'hnsw' in def_.lower():
                    hnsw_found = True
                    print(f"     ✅ HNSW Index detected: {def_}")
            
            if not hnsw_found:
                print("❌ HNSW Index NOT found!")
                # Optional: Offer to create it?
            else:
                print("✅ Performance optimization verified.")

    except Exception as e:
        print(f"❌ Error checking indexes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_indexes()
