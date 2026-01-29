import requests
import random
import string
import time

BASE_URL = "http://localhost:8000"

def generate_random_email():
    return f"test_user_{''.join(random.choices(string.ascii_lowercase, k=6))}@example.com"

def test_register():
    email = "noreply.ignasproyect@gmail.com" # Use the ONE email the user seems to control/check?
    # Or just use a dummy one and check logs.
    # To check "if it arrives", I need a real email.
    # The debug script sent to `noreply.ignasproyect@gmail.com` and it worked.
    # I should try to register with a variation to trigger the email sending.
    # Gmail ignores dots, but `+` works.
    
    # We can't register `noreply.ignasproyect@gmail.com` if it exists.
    # Let's use a random one and check ONLY the backend logs for "Verification email sent".
    email = generate_random_email()
    password = "Password123!" # Strong password
    
    print(f"Registering user: {email}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("Registration successful. Background task should be running.")
        else:
            print("Registration failed.")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_register()
