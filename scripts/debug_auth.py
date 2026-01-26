import sys
import os
# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.auth import authenticate_user, get_password_hash
from app.models import User
from sqlmodel import Session, select
from app.database import engine

print("Testing auth logic...")

try:
    with Session(engine) as session:
        # 1. Create a dummy user
        test_email = "debug_auth@example.com"
        test_pass = "secret123"
        
        # Cleanup
        existing = session.exec(select(User).where(User.email == test_email)).first()
        if existing:
            session.delete(existing)
            session.commit()
            
        hashed = get_password_hash(test_pass)
        user = User(email=test_email, hashed_password=hashed, role="user")
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"Created user: {user.email}")
        
        # 2. Authenticate
        auth_user = authenticate_user(session, test_email, test_pass)
        if auth_user:
            print("Authentication SUCCESS!")
        else:
            print("Authentication FAILED!")
            
        # 3. Test wrong password
        auth_user_wrong = authenticate_user(session, test_email, "wrongpass")
        if not auth_user_wrong:
            print("Wrong password check SUCCESS!")
        else:
            print("Wrong password check FAILED (Should not auth)!")
            
        # 4. Test non-existent user
        auth_user_none = authenticate_user(session, "nobody@nowhere.com", "pass")
        if not auth_user_none:
            print("Non-existent user check SUCCESS!")
            
        # Cleanup
        session.delete(user)
        session.commit()
        print("Cleanup done.")
        
except Exception as e:
    print(f"Auth test crashed: {e}")
    import traceback
    traceback.print_exc()
