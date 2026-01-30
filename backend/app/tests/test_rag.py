from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_requires_auth():
    """Test that the chat endpoint requires authentication."""
    response = client.post("/chat", json={"query": "test"})
    # Should return 401 Unauthorized without auth token
    assert response.status_code == 401
