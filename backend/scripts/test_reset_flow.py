import requests
import time
from sqlalchemy import create_engine, text
from app.config import settings

# Database setup to get token directly
engine = create_engine(settings.DATABASE_URL)
BASE_URL = "http://localhost:8000"

def test_reset_flow():
    email = "test_reset_flow@example.com"
    old_password = "OldPassword123!"
    new_password = "NewPassword123!" # Strong password
    
    # 1. Register or ensure user exists
    print(f"Creating/Checking user {email}...")
    requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": old_password})
    
    # 2. Request forgot password to generate token
    print("Requesting password reset token...")
    requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": email})
    
    # 3. Get token from DB manually
    with engine.connect() as conn:
        result = conn.execute(text("SELECT reset_token FROM users WHERE email = :email"), {"email": email})
        token = result.scalar()
        print(f"Token retrieved from DB: {token}")

    if not token:
        print("FAIL: No token found in DB")
        return

    # 4. Reset password via API
    print("Resetting password via API...")
    resp = requests.post(f"{BASE_URL}/auth/reset-password", json={
        "token": token,
        "new_password": new_password
    })
    print(f"Reset Response: {resp.status_code} - {resp.json()}")

    if resp.status_code != 200:
        print("FAIL: Password reset API failed")
        return

    # 5. Try Login with NEW password
    print("Attempting login with NEW password...")
    login_resp = requests.post(f"{BASE_URL}/auth/token", data={
        "username": email,
        "password": new_password
    })
    
    if login_resp.status_code == 200:
        print("SUCCESS: Login with new password worked!")
    else:
        print(f"FAIL: Login with new password failed. Status: {login_resp.status_code}")
        print(login_resp.json())

    # 6. Try Login with OLD password (should fail)
    print("Attempting login with OLD password (should fail)...")
    old_login_resp = requests.post(f"{BASE_URL}/auth/token", data={
        "username": email,
        "password": old_password
    })
    
    if old_login_resp.status_code != 200:
        print("SUCCESS: Login with old password rejected.")
    else:
        print("FAIL: Old password still works!")

if __name__ == "__main__":
    test_reset_flow()
