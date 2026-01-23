from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_chat_endpoint_mocked(mock_llm):
    """
    Test that the chat endpoint uses the mock LLM when in TEST mode.
    The mock_llm fixture (autouse=True) handles the patching if settings.USE_MOCK_LLM is True.
    """
    response = client.post("/api/v1/chat", json={"message": "Hola, esto es un test"})
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify we got the safe mocked response
    assert data["answer"] == "Respuesta simulada segura"
    
    # Verify the mock was actually called (if the fixture yielded the mock)
    if mock_llm:
        mock_llm.assert_called_once_with("Hola, esto es un test")
