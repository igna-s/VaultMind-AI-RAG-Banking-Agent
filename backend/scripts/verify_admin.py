import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_admin_access():
    print("🛡️ Testing Admin Access...")
    
    # Note: Since authentication is mocked in main.py:
    # get_current_user returns the first user found.
    # We already promoted 'admin@bank.com' (the first user usually) to 'admin' in the migration.
    # So this request should succeed if the server sees the db change.
    
    try:
        response = requests.get(f"{BASE_URL}/admin/users")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Admin Access Granted. Found {len(users)} users.")
            for u in users:
                print(f"   - {u.get('email')} ({u.get('role')})")
        else:
            print(f"❌ Admin Access Denied. Status: {response.status_code}")
            print(response.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_admin_access()
