import sys
import os
from sqlmodel import select, Session

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine
from app.models import User

def debug_user_role():
    print("🔍 Debugging User Role retrieval...")
    
    try:
        with Session(engine) as session:
            # 1. Fetch all users
            users = session.exec(select(User)).all()
            print(f"Found {len(users)} users.")
            
            for u in users:
                print(f"User: {u.email} | ID: {u.id}")
                # Try to access role
                try:
                    print(f"   Role attribute: {u.role}")
                except Exception as e:
                    print(f"   ❌ Error accessing role: {e}")
                    
            # 2. Check if admin exists specifically
            admin = session.exec(select(User).where(User.email == "admin@bank.com")).first()
            if admin:
                print(f"\n✅ Admin found: {admin.email}, Role: {admin.role}")
            else:
                print("\n❌ Admin 'admin@bank.com' NOT found.")

    except Exception as e:
        print(f"❌ Database Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_user_role()
