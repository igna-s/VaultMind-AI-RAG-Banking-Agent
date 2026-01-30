import pytest
from app.config import settings

# Simple fixtures for testing
# No complex mocking - tests should be straightforward

@pytest.fixture
def test_settings():
    """Expose settings for tests that need to check config."""
    return settings
