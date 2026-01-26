import os
import sys
from sqlmodel import select, Session
from sqlalchemy.orm import selectinload

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine
from app.models import User, Document, DocumentChunk, ChatSession, ChatMessage

def view_content():
    print("📊 Viewing Database Content (PostgreSQL Azure)")
    print("="*60)
    
    with Session(engine) as session:
        # 1. Users
        print("\n👥 USERS")
        users = session.exec(select(User)).all()
        for u in users:
            print(f"   ID: {u.id} | Email: {u.email} | Role: {u.role}")
            
        # 2. Key Documents & Chunks
        print("\n📄 DOCUMENTS & CHUNKS")
        # Load relationships
        docs = session.exec(select(Document).options(selectinload(Document.chunks))).all()
        if not docs:
            print("   (No documents found)")
        else:
            for d in docs:
                print(f"   [Doc ID: {d.id}] Title: '{d.title}' (User: {d.user_id})")
                print(f"      Path: {d.path_url}")
                for c in d.chunks:
                    print(f"      - Chunk {c.id}: {c.content[:50]}... [Vector Dim: {len(c.embedding)}]")
                    print(f"        Metadata: {c.chunk_metadata}")

        # 3. Chat History
        print("\n💬 CHAT SESSIONS")
        chat_sessions = session.exec(select(ChatSession).options(selectinload(ChatSession.messages))).all()
        if not chat_sessions:
            print("   (No chat sessions found)")
        else:
            for s in chat_sessions:
                print(f"   [Session ID: {s.id}] User: {s.user_id} | Title: {s.title}")
                for m in s.messages:
                    role_icon = "👤" if m.role == "user" else "🤖"
                    print(f"      {role_icon} {m.role}: {m.content[:80].replace(chr(10), ' ')}...")
                    if m.used_sources:
                        print(f"          🔗 Citations: {m.used_sources}")

    print("\n" + "="*60)

if __name__ == "__main__":
    view_content()
