import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlmodel import Session, select
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Env
load_dotenv()

# Force DATABASE_URL from args or env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL not set")
    sys.exit(1)

print(f"🔗 Connecting to DB: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '...'}")

try:
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        # 1. Test Vector Extension
        print("🔍 Testing Vector Extension...")
        try:
            session.exec(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'"))
            print("✅ 'vector' extension is installed.")
        except Exception as e:
            print(f"❌ 'vector' extension query failed: {e}")

        # 2. Test Embedding Generation (Voyage)
        print("\n🧠 Testing Voyage AI Embedding...")
        try:
            from app.services.rag import get_embedding
            # We need to make sure we use the keys from env
            if not os.getenv("VOYAGE_API_KEY"):
                print("❌ VOYAGE_API_KEY not found in env")
            
            emb = get_embedding("test query")
            print(f"✅ Embedding generated. Length: {len(emb)}")
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        # 3. Test RAG Search
        print("\n🔎 Testing RAG Search (pgvector)...")
        try:
            from app.models import DocumentChunk, Document
            # Create a vector of same length
            embedding = emb
            
            # Simple vector search query
            statement = text("""
                SELECT id, content, (embedding <=> :embedding) as distance
                FROM document_chunks
                ORDER BY distance ASC
                LIMIT 3
            """)
            
            results = session.exec(statement, params={"embedding": str(embedding)}).all()
            print(f"✅ Search successful. Found {len(results)} results.")
            for r in results:
                print(f"   - ID: {r[0]}, Dist: {r[2]:.4f}")
                
        except Exception as e:
            print(f"❌ RAG Search failed: {e}")
            import traceback
            traceback.print_exc()

        # 4. Test Groq Generation
        print("\n🤖 Testing Groq LLM Generation...")
        try:
            from app.services.llm import llm
            if not llm:
                print("❌ Groq LLM client not initialized (check GROQ_API_KEY)")
                sys.exit(1)
                
            print("   Invoking Groq...")
            response = llm.invoke("Hello, are you working?")
            print(f"✅ Groq Response: {response.content}")
        except Exception as e:
             print(f"❌ Groq failed: {e}")
             import traceback
             traceback.print_exc()


except Exception as e:
    print(f"❌ Global Error: {e}")
    import traceback
    traceback.print_exc()
