import os
import sys
from sqlalchemy import text

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine

def update_vector_dimension():
    print("📉 Updating embedding dimension from 1536 to 1024 (Voyage AI Standard)...")
    
    try:
        with engine.connect() as connection:
            # We need to drop the index first because it depends on the column type/opclass
            print("   Dropping existing HNSW index...")
            connection.execute(text("DROP INDEX IF EXISTS idx_chunks_embedding_hnsw;"))
            
            # Alter the column type
            # Note: This works easily if table is empty. If not, we'd need USING logic, but table is empty.
            print("   Altering column type to vector(1024)...")
            connection.execute(text("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1024);"))
            
            # Recreate the index
            print("   Recreating HNSW index...")
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw 
                ON document_chunks 
                USING hnsw (embedding vector_cosine_ops);
            """))
            
            connection.commit()
            print("✅ Successfully updated vector dimension to 1024.")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        # Validate if it failed because it's already 1024?
        # If so, we can ignore.
        if "dimension" in str(e): 
             pass
        else:
            sys.exit(1)

if __name__ == "__main__":
    update_vector_dimension()
