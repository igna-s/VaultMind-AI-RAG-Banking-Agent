import sys
import os
import logging
from sqlmodel import Session, select, delete

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import engine, init_db
from app.models import User, Document, DocumentChunk, ChatSession
from app.services.llm import generate_response
from app.services.rag import get_embedding, rag_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PipelineVerifier")

def verify_web_search():
    logger.info("--- Testing Web Search ---")
    query = "What is the current price of Bitcoin to the nearest dollar? (Just the number)"
    # Pass empty context to force web search
    result = generate_response(query, context_chunks=None, history=[])
    
    print(f"Query: {query}")
    print(f"Response: {result['response']}")
    print(f"Sources: {result['sources']}")
    
    if "Web Search" in str(result['sources']):
        logger.info("✅ Web Search Verified")
        return True
    else:
        logger.error("❌ Web Search Failed: Source not Web Search")
        return False

def verify_rag(session, user_id):
    logger.info("--- Testing RAG (Upload + Retrieve) ---")
    
    # 0. Setup Knowledge Base (Required for RAG Filter)
    from app.models import KnowledgeBase, UserKnowledgeBaseLink
    
    kb_name = "Test Knowledge Base"
    kb = session.exec(select(KnowledgeBase).where(KnowledgeBase.name == kb_name)).first()
    if not kb:
        kb = KnowledgeBase(name=kb_name, description="For testing", is_default=True)
        session.add(kb)
        session.commit()
        session.refresh(kb)
        
    # Ensure User is linked
    link = session.exec(select(UserKnowledgeBaseLink).where(
        UserKnowledgeBaseLink.user_id == user_id,
        UserKnowledgeBaseLink.knowledge_base_id == kb.id
    )).first()
    
    if not link:
        link = UserKnowledgeBaseLink(user_id=user_id, knowledge_base_id=kb.id)
        session.add(link)
        session.commit()

    # 1. Simulate Upload
    doc_title = "Secret Project Alpha"
    doc_content = "Project Alpha is a secret initiative to build a moon base made of cheese. The budget is 500 dollars."
    
    logger.info(f"Uploading Document: {doc_title} to KB: {kb.name}")
    
    # Cleanup previous run
    existing = session.exec(select(Document).where(Document.title == doc_title)).all()
    for doc_to_del in existing:
        # Manually delete chunks because cascade might not be configured
        existing_chunks = session.exec(select(DocumentChunk).where(DocumentChunk.document_id == doc_to_del.id)).all()
        for c in existing_chunks:
            session.delete(c)
        session.delete(doc_to_del)
    session.commit()
    
    # Create Doc WITH KB ID
    doc = Document(title=doc_title, user_id=user_id, type="text", path_url="mock", knowledge_base_id=kb.id)
    session.add(doc)
    session.commit()
    session.refresh(doc)
    
    # Create Chunk
    embedding = get_embedding(doc_content)
    chunk = DocumentChunk(
        document_id=doc.id,
        content=doc_content,
        embedding=embedding,
        chunk_index=0
    )
    session.add(chunk)
    session.commit()
    
    # 2. Retrieve
    query = "What is the budget of Project Alpha?"
    logger.info(f"Querying: {query}")
    
    # Manual RAG Pipeline call
    context_chunks = rag_pipeline(session, query, user_id)
    
    if not context_chunks:
        logger.error("❌ Retrieval Failed: No chunks found")
        return False
        
    logger.info(f"Retrieved {len(context_chunks)} chunks")
    print(f"Top Chunk: {context_chunks[0].content}")
    
    if "500 dollars" not in context_chunks[0].content:
         logger.error("❌ Retrieval Failed: Content mismatch")
         return False

    # 3. Generate Answer
    result = generate_response(query, context_chunks, history=[])
    print(f"LLM Answer: {result['response']}")
    
    if "500" in result['response'] or "dollars" in result['response']:
        logger.info("✅ RAG Answer Verified")
        return True
    else:
        logger.error("❌ RAG Answer Failed")
        return False

def main():
    init_db()
    with Session(engine) as session:
        # Get or create dummy user
        user = session.exec(select(User).where(User.email == "test@verify.com")).first()
        if not user:
            user = User(email="test@verify.com", hashed_password="pw", status="active", role="user")
            session.add(user)
            session.commit()
            session.refresh(user)
            
        print(f"User ID: {user.id}")
        
        web_ok = verify_web_search()
        print("\n")
        rag_ok = verify_rag(session, user.id)
        
        if web_ok and rag_ok:
            print("\n🎉 ALL SYSTEMS GO! The Agent is fully operational.")
            sys.exit(0)
        else:
            print("\n⚠️  Some systems failed.")
            sys.exit(1)

if __name__ == "__main__":
    main()
