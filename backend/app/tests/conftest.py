import pytest
from unittest.mock import AsyncMock
from backend.app.config import settings

@pytest.fixture(autouse=True)
def mock_llm(mocker):
    """
    Fixture to intercept LLM calls.
    If USE_MOCK_LLM is True, it patches the LLM service to return a safe mocked response.
    """
    if settings.USE_MOCK_LLM:
        # We Mock the specific function that handles LLM interaction.
        # Adjust the target path 'backend.app.main.get_llm_response' as needed if the code moves.
        mock = mocker.patch(
            "backend.app.main.get_llm_response",
            side_effect=AsyncMock(return_value="Respuesta simulada segura")
        )
        yield mock
    else:
        yield None
