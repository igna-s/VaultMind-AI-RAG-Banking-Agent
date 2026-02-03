from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the root endpoint returns 200 and expected message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Banking RAG API" in data["message"]
