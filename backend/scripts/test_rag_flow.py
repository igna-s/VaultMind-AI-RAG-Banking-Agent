import os
import sys
import requests
import json
import random

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://127.0.0.1:8000"

def test_rag_flow():
    print("🚀 Starting End-to-End RAG Test...")
    
    # 1. Create a "User" for testing (mocking auth by assuming user_id=1 exists or main.py creates it)
    # The main.py get_current_user defaults to admin@bank.com if no user.
    # We will use that default user for simplicity.
    
    # 2. Upload a Document
    print("\n📄 Step 1: Uploading Document...")
    doc_title = f"Test_Doc_{random.randint(1000,9999)}"
    doc_content = (
        "The Definitive Project is a revolutionary banking system designed in 2026. "
        "It uses hybrid RAG with PostgreSQL and pgvector. "
        "The primary AI agent is powered by Groq and the embeddings by Voyage AI. "
        "The project code is stored in /workspace/TheDefinitiveProyect."
    )
    
    url = f"{BASE_URL}/upload"
    params = {
        "title": doc_title,
        "content": doc_content,
        "folder_id": None # Root
    }
    
    try:
        response = requests.post(url, params=params) # FastAPI params in query for this endpoint def?
        # definition: def upload_document(title: str, content: str...
        # FastAPI default scalar arguments are query params.
        
        if response.status_code == 200:
            data = response.json()
            doc_id = data.get("doc_id")
            print(f"   ✅ Upload Successful! Doc ID: {doc_id}")
        else:
            print(f"   ❌ Upload Failed: {response.status_code} - {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"   ❌ Error connecting to server: {e}")
        print("   (Ensure uvicorn is running with --host 0.0.0.0)")
        sys.exit(1)

    # 3. Chat / Query
    print("\n💬 Step 2: Testing RAG Retrieval & Chat...")
    query = "What is The Definitive Project and what technologies does it use?"
    
    chat_url = f"{BASE_URL}/chat"
    payload = {
        "query": query,
        "session_id": None
    }
    
    try:
        response = requests.post(chat_url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response")
            sources = data.get("sources")
            
            print(f"   ✅ Chat Response Received!")
            print(f"   🤖 Answer: {answer}")
            print(f"   📚 Sources: {sources}")
            
            # Verification
            if doc_title in str(sources):
                print("   🎉 SUCCESS: The AI retrieved the document we just uploaded!")
            else:
                print("   ⚠️ WARNING: The AI did not cite the uploaded document. RAG retrieval might need tuning.")
                
        else:
            print(f"   ❌ Chat Failed: {response.status_code} - {response.text}")
            sys.exit(1)

    except Exception as e:
        print(f"   ❌ Error connecting to server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_rag_flow()
