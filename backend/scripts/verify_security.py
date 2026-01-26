from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.auth import get_password_hash
from app.database import get_session, engine
from sqlmodel import Session, select
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TestClient(app)

def test_security():
    # 1. Verify Admin Login
    logger.info("Testing Admin Login...")
    response = client.post(
        "/auth/token",
        data={"username": "admin@bank.com", "password": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        logger.info("\u2705 Admin login successful")
    else:
        logger.error(f"\u274C Admin login failed: {response.text}")
        return

    # 2. Test Rate Limiting on /chat
    logger.info("Testing Rate Limiting on /chat (Limit: 5/minute)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Hit 5 times (allowed)
    for i in range(5):
        # Using a dummy session ID to avoid 404/creation logic if possible, 
        # or just "New Chat" logic.
        # Check chat endpoint: it expects ChatRequest.
        # And if session_id is None, it finds 'General' or creates new.
        res = client.post(
            "/chat",
            json={"query": "test query"},
            headers=headers
        )
        if res.status_code != 200:
            logger.warning(f"Request {i+1} failed: {res.status_code}")
        else:
            logger.info(f"Request {i+1} allowed")

    # Hit 6th time (should fail)
    res = client.post(
            "/chat",
            json={"query": "test query"},
            headers=headers
    )
    if res.status_code == 429:
        logger.info("\u2705 Rate limiting working: Got 429 Too Many Requests")
    else:
        logger.error(f"\u274C Rate limiting failed: Got {res.status_code}")

if __name__ == "__main__":
    test_security()
